from datetime import UTC, datetime

from src.detector import SlidingWindowDetector


def _feed(detector: SlidingWindowDetector, symbol: str, prices: list[float]):
    now = datetime.now(UTC)
    signal = None
    for price in prices:
        signal = detector.observe(symbol, price, now)
    return signal


def test_warmup_never_flags():
    detector = SlidingWindowDetector(window_size=60, z_threshold=3.0, min_samples=10)
    signal = _feed(detector, "BTC", [100.0] * 5)
    assert signal is not None
    assert signal.is_anomaly is False
    assert signal.sample_size == 4


def test_stable_series_not_flagged():
    detector = SlidingWindowDetector(window_size=60, z_threshold=3.0, min_samples=10)
    signal = _feed(detector, "BTC", [100.0 + (index % 2) * 0.1 for index in range(30)])
    assert signal is not None
    assert signal.is_anomaly is False


def test_upside_spike_is_flagged():
    detector = SlidingWindowDetector(window_size=60, z_threshold=3.0, min_samples=10)
    now = datetime.now(UTC)
    for price in [100.0 + (index % 3) * 0.05 for index in range(30)]:
        detector.observe("BTC", price, now)

    spike = detector.observe("BTC", 130.0, now)
    assert spike.is_anomaly is True
    assert spike.direction == "spike_up"
    assert spike.z_score > 3.0
    assert spike.deviation_pct > 0


def test_downside_spike_direction():
    detector = SlidingWindowDetector(window_size=60, z_threshold=3.0, min_samples=10)
    now = datetime.now(UTC)
    for price in [100.0 + (index % 3) * 0.05 for index in range(30)]:
        detector.observe("BTC", price, now)

    crash = detector.observe("BTC", 70.0, now)
    assert crash.is_anomaly is True
    assert crash.direction == "spike_down"
    assert crash.z_score < -3.0


def test_per_symbol_isolation():
    detector = SlidingWindowDetector(window_size=60, z_threshold=3.0, min_samples=10)
    now = datetime.now(UTC)
    for _ in range(20):
        detector.observe("BTC", 100.0, now)

    # A brand new symbol has its own window and is still warming up.
    eth = detector.observe("ETH", 5000.0, now)
    assert eth.sample_size == 0
    assert eth.is_anomaly is False


def test_window_is_bounded():
    detector = SlidingWindowDetector(window_size=10, z_threshold=3.0, min_samples=5)
    now = datetime.now(UTC)
    for price in range(100):
        detector.observe("BTC", float(price), now)

    # Internal window never grows past window_size regardless of stream length.
    assert len(detector._windows["BTC"]) == 10
