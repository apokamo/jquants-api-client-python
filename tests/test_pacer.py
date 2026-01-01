"""Sub-Phase 3.1.5 TDD tests: Pacer (Leaky Bucket rate limiter)."""

import threading
import time
from unittest.mock import patch

import pytest


class TestPacerInterval:
    """Test Pacer interval calculation (PACER-001, PACER-002)."""

    def test_rate_120_gives_interval_0_5(self):
        """PACER-001: rate=120 → interval=0.5秒"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=120)
        assert pacer.interval == pytest.approx(0.5, rel=1e-6)

    def test_rate_5_gives_interval_12(self):
        """PACER-002: rate=5 → interval=12秒"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=5)
        assert pacer.interval == pytest.approx(12.0, rel=1e-6)

    def test_rate_60_gives_interval_1(self):
        """rate=60 → interval=1.0秒"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=60)
        assert pacer.interval == pytest.approx(1.0, rel=1e-6)

    def test_rate_1_gives_interval_60(self):
        """rate=1 → interval=60秒"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=1)
        assert pacer.interval == pytest.approx(60.0, rel=1e-6)


class TestPacerValidation:
    """Test Pacer parameter validation (PACER-003)."""

    def test_rate_zero_raises_valueerror(self):
        """PACER-003: rate=0 → ValueError"""
        from jquants.pacer import Pacer

        with pytest.raises(ValueError) as exc_info:
            Pacer(rate=0)
        assert "rate" in str(exc_info.value).lower()

    def test_rate_negative_raises_valueerror(self):
        """PACER-003: rate=-1 → ValueError"""
        from jquants.pacer import Pacer

        with pytest.raises(ValueError) as exc_info:
            Pacer(rate=-1)
        assert "rate" in str(exc_info.value).lower()

    def test_rate_negative_large_raises_valueerror(self):
        """PACER-003: rate=-100 → ValueError"""
        from jquants.pacer import Pacer

        with pytest.raises(ValueError) as exc_info:
            Pacer(rate=-100)
        assert "rate" in str(exc_info.value).lower()


class TestPacerFirstWait:
    """Test Pacer first wait behavior (PACER-004)."""

    def test_first_wait_returns_zero(self):
        """PACER-004: 初回wait() → 待機時間=0"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=60)
        waited = pacer.wait()
        assert waited == pytest.approx(0.0, abs=0.01)

    def test_first_wait_is_immediate(self):
        """PACER-004: 初回wait()は即時発行"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=1)  # 60秒間隔
        start = time.monotonic()
        pacer.wait()
        elapsed = time.monotonic() - start
        # 初回は即時（0.1秒未満で完了すべき）
        assert elapsed < 0.1


@pytest.mark.slow
class TestPacerConsecutiveWait:
    """Test Pacer consecutive wait behavior (PACER-005)."""

    def test_consecutive_waits_maintain_interval(self):
        """PACER-005: 連続wait() → 間隔維持"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=120)  # 0.5秒間隔

        # 初回
        pacer.wait()

        # 2回目は0.5秒待機
        start = time.monotonic()
        waited = pacer.wait()
        elapsed = time.monotonic() - start

        # 0.5秒 ± 0.1秒の範囲
        assert waited >= 0.4
        assert elapsed >= 0.4

    def test_consecutive_waits_multiple_times(self):
        """PACER-005: 複数回連続wait()でも間隔維持"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=120)  # 0.5秒間隔

        start_total = time.monotonic()

        # 3回連続でwait
        pacer.wait()  # 初回：即時
        pacer.wait()  # 2回目：0.5秒待機
        pacer.wait()  # 3回目：0.5秒待機

        total_elapsed = time.monotonic() - start_total

        # 最低でも約1.0秒（0.5 + 0.5）経過すべき
        assert total_elapsed >= 0.9


@pytest.mark.slow
class TestPacerElapsedTime:
    """Test Pacer elapsed time consideration (PACER-006)."""

    def test_wait_after_interval_is_immediate(self):
        """PACER-006: 間隔経過後wait() → 待機時間=0"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=120)  # 0.5秒間隔

        pacer.wait()  # 初回
        time.sleep(0.6)  # 間隔以上待つ

        start = time.monotonic()
        waited = pacer.wait()
        elapsed = time.monotonic() - start

        # 即時発行されるべき
        assert waited < 0.1
        assert elapsed < 0.1

    def test_wait_partial_elapsed_waits_remaining(self):
        """PACER-006: 間隔未満経過 → 残り時間だけ待機"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=120)  # 0.5秒間隔

        pacer.wait()  # 初回
        time.sleep(0.2)  # 0.2秒経過

        start = time.monotonic()
        waited = pacer.wait()
        elapsed = time.monotonic() - start

        # 約0.3秒待機すべき（0.5 - 0.2 = 0.3）
        assert waited >= 0.2
        assert elapsed >= 0.2


class TestPacerReset:
    """Test Pacer reset behavior (PACER-007)."""

    def test_reset_makes_next_wait_immediate(self):
        """PACER-007: reset() → 次回即時"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=120)  # 0.5秒間隔

        pacer.wait()  # 初回
        # 通常ならここで wait() すると0.5秒待機

        pacer.reset()  # リセット

        start = time.monotonic()
        waited = pacer.wait()
        elapsed = time.monotonic() - start

        # リセット後は初回扱い → 即時
        assert waited < 0.05
        assert elapsed < 0.1


@pytest.mark.slow
class TestPacerThreadSafety:
    """Test Pacer thread safety (PACER-008)."""

    def test_concurrent_waits_maintain_interval(self):
        """PACER-008: 複数スレッドから同時wait() → 競合なし"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=60)  # 1秒間隔
        timestamps: list[float] = []
        lock = threading.Lock()

        def worker():
            pacer.wait()
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

    def test_concurrent_waits_no_deadlock(self):
        """PACER-008: 並列アクセスでデッドロックしない"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=1000)  # 高速（0.06秒間隔）
        completed = []
        lock = threading.Lock()

        def worker(worker_id: int):
            for _ in range(5):
                pacer.wait()
            with lock:
                completed.append(worker_id)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]

        for t in threads:
            t.start()

        # 10秒以内に完了すべき（デッドロックしていなければ）
        for t in threads:
            t.join(timeout=10)
            assert not t.is_alive(), "Thread did not complete - possible deadlock"

        assert len(completed) == 5

    def test_concurrent_waits_total_time_consistent(self):
        """PACER-008: 並列時の合計待機時間が理論値と一致"""
        from jquants.pacer import Pacer

        pacer = Pacer(rate=120)  # 0.5秒間隔

        num_workers = 4
        wait_times: list[float] = []
        lock = threading.Lock()

        def worker():
            waited = pacer.wait()
            with lock:
                wait_times.append(waited)

        threads = [threading.Thread(target=worker) for _ in range(num_workers)]

        start_time = time.monotonic()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        total_elapsed = time.monotonic() - start_time

        # 4リクエストで3間隔 → 最低1.5秒（0.5 * 3）
        # 実際には並列起動のオーバーヘッドがあるので少し余裕を見る
        assert total_elapsed >= 1.3


class TestPacerMockedTime:
    """Test Pacer with mocked time for precise control."""

    def test_wait_calculation_precise(self):
        """wait()の計算が正確"""
        from jquants.pacer import Pacer

        with patch("time.monotonic") as mock_time:
            with patch("time.sleep") as mock_sleep:
                mock_time.return_value = 100.0

                pacer = Pacer(rate=60)  # 1秒間隔

                # 初回
                waited = pacer.wait()
                assert waited == 0.0
                mock_sleep.assert_not_called()

                # 2回目（0.3秒経過）
                mock_time.return_value = 100.3
                waited = pacer.wait()
                # 1.0 - 0.3 = 0.7秒待機
                mock_sleep.assert_called_once()
                assert mock_sleep.call_args[0][0] == pytest.approx(0.7, rel=1e-6)

    def test_wait_no_sleep_when_elapsed_exceeds_interval(self):
        """間隔以上経過後は sleep しない"""
        from jquants.pacer import Pacer

        with patch("time.monotonic") as mock_time:
            with patch("time.sleep") as mock_sleep:
                mock_time.return_value = 100.0

                pacer = Pacer(rate=60)  # 1秒間隔

                # 初回
                pacer.wait()

                # 2回目（2秒経過 - 間隔の2倍）
                mock_time.return_value = 102.0
                waited = pacer.wait()

                assert waited == 0.0
                mock_sleep.assert_not_called()
