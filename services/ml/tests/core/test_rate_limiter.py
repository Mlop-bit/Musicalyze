import pytest

from ml.core.rate_limiter import TokenBucket


class FakeTime:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def _bucket(fake_time: FakeTime, capacity: int, refill_per_second: float) -> TokenBucket:
    return TokenBucket(
        capacity=capacity,
        refill_per_second=refill_per_second,
        clock=fake_time.clock,
        sleep=fake_time.sleep,
    )


def test_acquire_does_not_wait_while_tokens_remain() -> None:
    fake_time = FakeTime()
    bucket = _bucket(fake_time, capacity=3, refill_per_second=1.0)

    for _ in range(3):
        bucket.acquire()

    assert fake_time.sleeps == []


def test_acquire_waits_for_the_refill_once_the_bucket_is_empty() -> None:
    fake_time = FakeTime()
    bucket = _bucket(fake_time, capacity=1, refill_per_second=2.0)

    bucket.acquire()
    bucket.acquire()

    assert fake_time.sleeps == [pytest.approx(0.5)]


def test_acquire_spaces_consecutive_calls_by_the_refill_interval() -> None:
    fake_time = FakeTime()
    bucket = _bucket(fake_time, capacity=1, refill_per_second=1.0)

    for _ in range(4):
        bucket.acquire()

    assert fake_time.now == pytest.approx(3.0)


def test_idle_time_refills_the_bucket_up_to_its_capacity() -> None:
    fake_time = FakeTime()
    bucket = _bucket(fake_time, capacity=2, refill_per_second=1.0)
    bucket.acquire()
    bucket.acquire()

    fake_time.now += 100.0
    for _ in range(2):
        bucket.acquire()
    bucket.acquire()

    assert fake_time.sleeps == [pytest.approx(1.0)]


@pytest.mark.parametrize(("capacity", "refill_per_second"), [(0, 1.0), (1, 0.0), (1, -1.0)])
def test_bucket_rejects_non_positive_parameters(capacity: int, refill_per_second: float) -> None:
    with pytest.raises(ValueError, match="must be positive"):
        TokenBucket(capacity=capacity, refill_per_second=refill_per_second)
