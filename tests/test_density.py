import pytest
from backend.vision.density import DensityCalculator

def test_density_thresholds():
    cfg = {"low_density": 5, "medium_density": 10}
    calc = DensityCalculator(cfg)

    # LOW
    assert calc.calculate(0) == "LOW"
    assert calc.calculate(3) == "LOW"
    assert calc.calculate(5) == "LOW"

    # MEDIUM
    assert calc.calculate(6) == "MEDIUM"
    assert calc.calculate(8) == "MEDIUM"
    assert calc.calculate(10) == "MEDIUM"

    # HIGH
    assert calc.calculate(11) == "HIGH"
    assert calc.calculate(20) == "HIGH"
