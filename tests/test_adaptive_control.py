import pytest

from backend.decision.adaptive_control import AdaptiveTrafficController


@pytest.fixture
def controller():
    return AdaptiveTrafficController({
        "normal_green_time": 10,
        "high_density_green_time": 20,
        "min_green_time": 6,
        "max_green_time": 18,
        "medium_axis_count": 4,
        "high_axis_count": 8,
    })


def test_green_time_uses_each_axis_demand_not_total_density(controller):
    counts = {"NORTH": 7, "SOUTH": 2, "EAST": 1, "WEST": 0}

    assert controller.calculate_green_time("HIGH", 10, counts, "NS") == 18
    assert controller.calculate_green_time("HIGH", 10, counts, "EW") == 10


def test_green_time_respects_bounds(controller):
    counts = {"NORTH": 0, "SOUTH": 0, "EAST": 0, "WEST": 0}
    controller.normal_green = 3
    assert controller.calculate_green_time("LOW", 0, counts, "NS") == 6

    controller.normal_green = 40
    assert controller.calculate_green_time("LOW", 0, counts, "EW") == 18


def test_green_time_rejects_unknown_axis(controller):
    with pytest.raises(ValueError, match="Unsupported traffic axis"):
        controller.calculate_green_time("LOW", 0, {}, "NORTH")
