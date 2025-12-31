"""Leaky Bucket rate limiter for J-Quants API V2."""

import threading
import time


class Pacer:
    """Leaky Bucket方式のレートリミッター.

    一定間隔でリクエストを整流化し、バーストを一切許容しない。
    """

    def __init__(self, rate: int) -> None:
        """Initialize Pacer.

        Args:
            rate: 1分あたりの最大リクエスト数 (req/min)

        Raises:
            ValueError: rate <= 0 の場合
        """
        if rate <= 0:
            raise ValueError(f"rate must be positive, got {rate}")

        self._rate = rate
        self._interval = 60.0 / rate
        self._last_request_time: float | None = None
        self._lock = threading.Lock()

    @property
    def interval(self) -> float:
        """リクエスト間隔（秒）."""
        return self._interval

    def wait(self) -> float:
        """次のリクエストまで待機する.

        Returns:
            実際に待機した時間（秒）

        Note:
            - 初回は即時（待機時間=0）
            - スレッドセーフであること
        """
        with self._lock:
            now = time.monotonic()

            # 初回は即時発行
            if self._last_request_time is None:
                self._last_request_time = now
                return 0.0

            # 前回リクエストからの経過時間
            elapsed = now - self._last_request_time
            wait_time = self._interval - elapsed

            if wait_time > 0:
                time.sleep(wait_time)
                self._last_request_time = time.monotonic()
                return wait_time
            else:
                # 間隔以上経過している場合は即時
                self._last_request_time = now
                return 0.0

    def reset(self) -> None:
        """状態をリセットする（テスト用）."""
        with self._lock:
            self._last_request_time = None
