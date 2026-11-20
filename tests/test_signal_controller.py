import pytest
from backend.decision.signal_controller import SignalController

def test_signal_transition_is_safe():
    traffic_cfg = {
        "normal_green_time": 10,
        "yellow_time": 3,
        "all_red_time": 1
    }
    controller = SignalController(traffic_cfg)
    t = 0.0

    # Initial state: NS_GREEN
    state = controller.update(t, {"is_emergency": False, "mode": "NORMAL"}, 10)
    assert state["state"] == "NS_GREEN"
    assert state["signals"]["NORTH"] == "GREEN"
    assert state["signals"]["EAST"] == "RED"

    # After 10 seconds: must transition to NS_YELLOW, NOT directly to EW_GREEN
    t = 10.1
    state = controller.update(t, {"is_emergency": False, "mode": "NORMAL"}, 10)
    assert state["state"] == "NS_YELLOW"
    assert state["signals"]["NORTH"] == "YELLOW"
    assert state["signals"]["EAST"] == "RED"

    # After yellow duration (3s): must enter ALL_RED clearance buffer
    t = 13.2
    state = controller.update(t, {"is_emergency": False, "mode": "NORMAL"}, 10)
    assert state["state"] == "ALL_RED_1"
    assert state["signals"]["NORTH"] == "RED"
    assert state["signals"]["EAST"] == "RED"

    # After all red (1s): now EW_GREEN
    t = 14.3
    state = controller.update(t, {"is_emergency": False, "mode": "NORMAL"}, 10)
    assert state["state"] == "EW_GREEN"
    assert state["signals"]["NORTH"] == "RED"
    assert state["signals"]["EAST"] == "GREEN"

def test_emergency_preemption_safety():
    traffic_cfg = {"normal_green_time": 10, "yellow_time": 3, "all_red_time": 1}
    controller = SignalController(traffic_cfg)

    # Force EW_GREEN
    controller.state = "EW_GREEN"
    controller.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "GREEN", "WEST": "GREEN"}
    controller.allocated_duration = 10
    controller.state_start_time = 0.0

    # Emergency arrives from NORTH
    eval_emergency = {
        "is_emergency": True,
        "mode": "EMERGENCY",
        "target_direction": "NORTH"
    }

    state = controller.update(1.0, eval_emergency, 10)
    # Because EW currently has GREEN, controller MUST initiate EW_YELLOW clearance first!
    assert state["state"] == "EW_YELLOW"
    assert state["signals"]["EAST"] == "YELLOW"
    assert state["signals"]["NORTH"] == "RED"


def test_each_axis_receives_its_own_green_duration():
    controller = SignalController({
        "normal_green_time": 10,
        "yellow_time": 3,
        "all_red_time": 1
    })
    green_times = {"NS": 20, "EW": 12}

    state = controller.update(0.0, {"is_emergency": False, "mode": "NORMAL"}, green_times)
    assert state["allocated_seconds"] == 20

    controller.update(20.1, {"is_emergency": False, "mode": "NORMAL"}, green_times)
    controller.update(23.2, {"is_emergency": False, "mode": "NORMAL"}, green_times)
    state = controller.update(24.3, {"is_emergency": False, "mode": "NORMAL"}, green_times)

    assert state["state"] == "EW_GREEN"
    assert state["allocated_seconds"] == 12


def test_low_demand_axis_still_gets_a_green_turn():
    controller = SignalController({
        "normal_green_time": 10,
        "yellow_time": 3,
        "all_red_time": 1
    })
    green_times = {"NS": 20, "EW": 6}
    controller.update(0.0, {"is_emergency": False, "mode": "NORMAL"}, green_times)
    controller.update(20.1, {"is_emergency": False, "mode": "NORMAL"}, green_times)
    controller.update(23.2, {"is_emergency": False, "mode": "NORMAL"}, green_times)
    state = controller.update(24.3, {"is_emergency": False, "mode": "NORMAL"}, green_times)

    assert state["signals"]["EAST"] == "GREEN"
    assert state["signals"]["WEST"] == "GREEN"
    assert state["allocated_seconds"] == 6
