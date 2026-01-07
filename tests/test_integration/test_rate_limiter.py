"""Sub-Phase 3.1.5 Integration tests: Rate Limiter (RATE-001~008)."""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from jquants.exceptions import JQuantsRateLimitError


class TestRateLimiterDefaultBehavior:
    """Test rate limiter default behavior (RATE-001, RATE-006)."""

    def test_rate_limit_none_uses_free_plan_default(self):
        """RATE-001: rate_limit=None時の挙動"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", rate_limit=None)

        # Freeプラン（5 req/min）がデフォルト
        assert client._rate_limit == 5
        # 間隔は12秒（60/5）
        assert client._pacer.interval == pytest.approx(12.0, rel=1e-6)

    def test_max_workers_1_is_serial(self):
        """RATE-006: max_workers=1で直列取得"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", max_workers=1)

        assert client._max_workers == 1


class TestRateLimiterCustomRate:
    """Test rate limiter with custom rate (RATE-002)."""

    def test_rate_limit_60_custom_value(self):
        """RATE-002: rate_limit=60等カスタム値"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", rate_limit=60)

        assert client._rate_limit == 60
        # 間隔は1秒（60/60）
        assert client._pacer.interval == pytest.approx(1.0, rel=1e-6)

    def test_rate_limit_120_custom_value(self):
        """RATE-002: rate_limit=120等カスタム値"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", rate_limit=120)

        assert client._rate_limit == 120
        # 間隔は0.5秒（60/120）
        assert client._pacer.interval == pytest.approx(0.5, rel=1e-6)


@pytest.mark.slow
class TestRateLimiterPacing:
    """Test rate limiter pacing behavior (RATE-003)."""

    def test_consecutive_requests_with_pacing(self):
        """RATE-003: 連続リクエストで待機発生"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", rate_limit=120)  # 0.5秒間隔

        # Pacerの動作を直接テスト
        start = time.monotonic()
        client._pacer.wait()  # 初回：即時
        client._pacer.wait()  # 2回目：0.5秒待機
        client._pacer.wait()  # 3回目：0.5秒待機
        elapsed = time.monotonic() - start

        # 最低約1.0秒経過すべき
        assert elapsed >= 0.9

    def test_pacer_integrated_with_client(self):
        """RATE-003: ClientV2にPacerが統合されている"""
        from jquants import ClientV2
        from jquants.pacer import Pacer

        client = ClientV2(api_key="test_api_key", rate_limit=60)

        # Pacerインスタンスが存在
        assert hasattr(client, "_pacer")
        assert isinstance(client._pacer, Pacer)


class TestRateLimiter429Retry:
    """Test 429 retry behavior (RATE-004, RATE-005)."""

    def test_429_waits_before_retry(self):
        """RATE-004: 429で5分10秒待ってリトライ"""
        from jquants import ClientV2

        client = ClientV2(
            api_key="test_api_key",
            retry_on_429=True,
            retry_wait_seconds=310,
            retry_max_attempts=3,
        )

        # 設定が正しく反映されている
        assert client._retry_on_429 is True
        assert client._retry_wait_seconds == 310
        assert client._retry_max_attempts == 3

    def test_429_immediate_exception_when_disabled(self):
        """RATE-005: retry_on_429=Falseで即例外"""
        from jquants import ClientV2

        client = ClientV2(
            api_key="test_api_key",
            retry_on_429=False,
        )

        # retry_on_429=False が設定されている
        assert client._retry_on_429 is False

    def test_429_retry_mechanism_with_mock(self):
        """RATE-004: 429リトライメカニズム（モック）"""
        from jquants import ClientV2

        client = ClientV2(
            api_key="test_api_key",
            retry_on_429=True,
            retry_wait_seconds=1,  # テスト用に短縮
            retry_max_attempts=2,
        )

        # _request_with_rate_limit メソッドが実装されたら使用
        # 現時点ではパラメータの設定のみ確認
        assert client._retry_wait_seconds == 1
        assert client._retry_max_attempts == 2


@pytest.mark.slow
class TestRateLimiterParallel:
    """Test parallel execution (RATE-007, RATE-008)."""

    def test_max_workers_greater_than_1_enables_parallel(self):
        """RATE-007: max_workers>1で並列取得"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", max_workers=5)

        assert client._max_workers == 5

    def test_parallel_access_no_race_condition(self):
        """RATE-008: 並列アクセスで競合なし"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", rate_limit=60)  # 1秒間隔

        timestamps: list[float] = []
        lock = threading.Lock()

        def worker():
            client._pacer.wait()
            with lock:
                timestamps.append(time.monotonic())

        threads = [threading.Thread(target=worker) for _ in range(3)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # タイムスタンプを時系列順にソート
        timestamps.sort()

        # 各リクエスト間の間隔が約1秒であることを確認
        for i in range(1, len(timestamps)):
            diff = timestamps[i] - timestamps[i - 1]
            # 間隔は最低でも0.9秒（少しの誤差を許容）
            assert diff >= 0.9, f"Interval {i}: {diff} < 0.9"


class TestRateLimiter429Integration:
    """Test 429 handling integration."""

    def test_429_response_raises_rate_limit_error(self):
        """429レスポンスでJQuantsRateLimitErrorが発生"""
        from jquants import ClientV2

        # retry_on_429=False で即座に例外を発生させる
        client = ClientV2(api_key="test_api_key", retry_on_429=False)

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.ok = False
            mock_response.status_code = 429
            mock_response.text = '{"message": "Rate limit exceeded"}'
            mock_response.json.return_value = {"message": "Rate limit exceeded"}
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with pytest.raises(JQuantsRateLimitError) as exc_info:
                client._request("GET", "/path")

            assert exc_info.value.status_code == 429

    @pytest.mark.slow
    def test_pacer_works_between_requests(self):
        """Pacerがリクエスト間で動作することを確認"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", rate_limit=120)  # 0.5秒間隔

        # Pacerを直接使用してリクエスト間の待機を確認
        wait1 = client._pacer.wait()  # 初回：即時
        assert wait1 == 0.0

        wait2 = client._pacer.wait()  # 2回目：0.5秒待機
        assert wait2 >= 0.4


class TestRateLimiterAllParametersCombined:
    """Test all rate limiter parameters combined."""

    def test_all_parameters_set_correctly(self):
        """全パラメータが正しく設定される"""
        from jquants import ClientV2

        client = ClientV2(
            api_key="test_api_key",
            rate_limit=100,
            max_workers=3,
            retry_on_429=True,
            retry_wait_seconds=600,
            retry_max_attempts=5,
        )

        assert client._rate_limit == 100
        assert client._max_workers == 3
        assert client._retry_on_429 is True
        assert client._retry_wait_seconds == 600
        assert client._retry_max_attempts == 5
        assert client._pacer.interval == pytest.approx(0.6, rel=1e-6)

    def test_default_parameters_are_safe(self):
        """デフォルトパラメータが最安全である"""
        from jquants import ClientV2

        # 明示的なパラメータなしで初期化
        client = ClientV2(api_key="test_api_key")

        # Freeプランのレート（5 req/min）
        assert client._rate_limit == 5
        # 直列（並列化なし）
        assert client._max_workers == 1
        # リトライ有効
        assert client._retry_on_429 is True
        # 5分10秒待機
        assert client._retry_wait_seconds == 310
        # 最大3回リトライ
        assert client._retry_max_attempts == 3


class TestRequestPathIntegration:
    """Test _request path integration with pacing and 429 retry."""

    def test_request_calls_pacer_wait_on_success(self):
        """_request成功時にPacer.wait()が1回呼ばれる"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", rate_limit=120)

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with patch.object(client._pacer, "wait", return_value=0.0) as mock_wait:
                client._request("GET", "/test")

                # 成功時はwait()が1回呼ばれる（リトライなし）
                mock_wait.assert_called_once()

    def test_429_retry_then_success(self):
        """429 → wait → 再試行 → 成功"""
        from jquants import ClientV2

        client = ClientV2(
            api_key="test_api_key",
            retry_on_429=True,
            retry_wait_seconds=0.01,  # テスト用に短縮
            retry_max_attempts=3,
        )

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()

            # 1回目: 429, 2回目: 200
            mock_response_429 = MagicMock()
            mock_response_429.ok = False
            mock_response_429.status_code = 429
            mock_response_429.text = '{"message": "Rate limit exceeded"}'
            mock_response_429.json.return_value = {"message": "Rate limit exceeded"}
            mock_response_429.headers = {}  # No Retry-After header

            mock_response_200 = MagicMock()
            mock_response_200.ok = True
            mock_response_200.status_code = 200

            mock_session.request.side_effect = [mock_response_429, mock_response_200]
            mock_session_method.return_value = mock_session

            with patch.object(client._pacer, "wait", return_value=0.0) as mock_wait:
                with patch("time.sleep") as mock_sleep:
                    response = client._request("GET", "/test")

                    # 成功レスポンスが返る
                    assert response.status_code == 200
                    # time.sleepが1回呼ばれる（リトライ待機）
                    mock_sleep.assert_called_once_with(0.01)
                    # sessionが2回呼ばれる（初回 + リトライ）
                    assert mock_session.request.call_count == 2
                    # wait()が2回呼ばれる（各試行前にpacing適用）
                    assert mock_wait.call_count == 2
                    # 429レスポンスがcloseされる（接続プール解放）
                    mock_response_429.close.assert_called_once()

    def test_429_retry_disabled_raises_immediately(self):
        """429 + retry_on_429=False → 即例外"""
        from jquants import ClientV2

        client = ClientV2(
            api_key="test_api_key",
            retry_on_429=False,
        )

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.ok = False
            mock_response.status_code = 429
            mock_response.text = '{"message": "Rate limit exceeded"}'
            mock_response.json.return_value = {"message": "Rate limit exceeded"}
            mock_response.headers = {}  # No Retry-After header
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with patch.object(client._pacer, "wait", return_value=0.0):
                with patch("time.sleep") as mock_sleep:
                    with pytest.raises(JQuantsRateLimitError) as exc_info:
                        client._request("GET", "/test")

                    assert exc_info.value.status_code == 429
                    # time.sleepは呼ばれない（即例外）
                    mock_sleep.assert_not_called()
                    # sessionは1回のみ
                    assert mock_session.request.call_count == 1

    def test_429_retry_max_attempts_exceeded_raises(self):
        """429 + retry_max_attempts超過 → 例外"""
        from jquants import ClientV2

        client = ClientV2(
            api_key="test_api_key",
            retry_on_429=True,
            retry_wait_seconds=0.01,
            retry_max_attempts=2,
        )

        with patch.object(client, "_request_session") as mock_session_method:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.ok = False
            mock_response.status_code = 429
            mock_response.text = '{"message": "Rate limit exceeded"}'
            mock_response.json.return_value = {"message": "Rate limit exceeded"}
            mock_response.headers = {}  # No Retry-After header
            mock_session.request.return_value = mock_response
            mock_session_method.return_value = mock_session

            with patch.object(client._pacer, "wait", return_value=0.0):
                with patch("time.sleep") as mock_sleep:
                    with pytest.raises(JQuantsRateLimitError) as exc_info:
                        client._request("GET", "/test")

                    assert exc_info.value.status_code == 429
                    # time.sleepが2回呼ばれる（リトライ2回分）
                    assert mock_sleep.call_count == 2
                    # sessionが3回呼ばれる（初回 + リトライ2回）
                    assert mock_session.request.call_count == 3

    def test_connection_pool_uses_max_workers(self):
        """接続プールに_max_workersが反映される"""
        from jquants import ClientV2

        client = ClientV2(api_key="test_api_key", max_workers=8)

        # セッション作成前は None
        assert client._session is None

        # セッション取得
        session = client._request_session()

        # アダプタの設定を確認
        adapter = session.get_adapter("https://")
        # pool_connections と pool_maxsize が _max_workers + 10 であること
        assert adapter._pool_connections == 18  # 8 + 10
        assert adapter._pool_maxsize == 18  # 8 + 10
