from fastapi import APIRouter, Request, UploadFile, File
from typing import Dict, Any

demo_router = APIRouter(prefix="/api/demo", tags=["Demo Mode Simulation"])

def _scenario_from_files(video: UploadFile | None, audio: UploadFile | None) -> str:
    file_names = " ".join(
        file.filename.lower() for file in (video, audio) if file and file.filename
    )
    if any(word in file_names for word in ("accident", "crash", "collision", "impact")):
        return "accident"
    if "fire" in file_names:
        return "fire-truck"
    if "police" in file_names:
        return "police"
    if any(word in file_names for word in ("heavy", "traffic", "congestion")):
        return "heavy-traffic"
    if any(word in file_names for word in ("ambulance", "emergency", "siren")):
        return "ambulance"
    return "normal"

@demo_router.post("/upload")
async def demo_upload(
    request: Request,
    video: UploadFile | None = File(default=None),
    audio: UploadFile | None = File(default=None),
):
    """Uses uploaded media names as software-demo scenario inputs.

    The production camera and microphone pipelines remain untouched. This endpoint
    feeds the same deterministic demo overrides used by the presentation controls.
    """
    if video is None and audio is None:
        return {"status": "error", "message": "Upload a video, an audio file, or both."}

    scenario = _scenario_from_files(video, audio)
    scenario_handlers = {
        "ambulance": demo_ambulance,
        "fire-truck": demo_fire_truck,
        "police": demo_police,
        "heavy-traffic": demo_heavy_traffic,
        "accident": demo_accident,
        "normal": demo_normal,
    }
    response = await scenario_handlers[scenario](request)
    return {
        **response,
        "source": "UPLOADED_MEDIA",
        "video_file": video.filename if video else None,
        "audio_file": audio.filename if audio else None,
    }

@demo_router.post("/normal")
async def demo_normal(request: Request):
    """Sets routine light traffic flow."""
    app_state = request.app.state
    app_state.vision_pipeline.set_demo_override(False)
    app_state.audio_pipeline.set_demo_override(False)
    return {"status": "success", "scenario": "NORMAL_TRAFFIC", "mode": "LIVE"}

@demo_router.post("/heavy-traffic")
async def demo_heavy_traffic(request: Request):
    """Simulates high vehicle congestion (14 vehicles) to demonstrate Adaptive Green extension."""
    app_state = request.app.state
    app_state.audio_pipeline.set_demo_override(True, {
        "class": "heavy_honking",
        "confidence": 0.88
    })
    app_state.vision_pipeline.set_demo_override(True, {
        "counts": {"car": 9, "motorcycle": 3, "bus": 1, "truck": 1, "ambulance": 0, "total": 14},
        "density": "HIGH",
        "ambulance_detected": False,
        "direction_counts": {"NORTH": 8, "SOUTH": 4, "EAST": 1, "WEST": 1}
    })
    return {"status": "success", "scenario": "HEAVY_TRAFFIC", "expected": "Adaptive Green Extension (+10-15s)"}

@demo_router.post("/ambulance")
async def demo_ambulance(request: Request):
    """Simulates Case 1: Ambulance siren (95%) + Visual Ambulance (92%) -> Green Corridor."""
    app_state = request.app.state
    app_state.audio_pipeline.set_demo_override(True, {
        "class": "ambulance_siren",
        "confidence": 0.95
    })
    app_state.vision_pipeline.set_demo_override(True, {
        "counts": {"car": 4, "motorcycle": 1, "bus": 0, "truck": 0, "ambulance": 1, "total": 6},
        "density": "MEDIUM",
        "ambulance_detected": True,
        "ambulance_confidence": 0.92,
        "ambulance_direction": "NORTH",
        "direction_counts": {"NORTH": 3, "SOUTH": 1, "EAST": 1, "WEST": 1}
    })
    return {"status": "success", "scenario": "AMBULANCE_DUAL_CONFIRMATION", "expected": "Emergency Green Corridor NORTH"}

@demo_router.post("/fire-truck")
async def demo_fire_truck(request: Request):
    """Simulates Fire Truck siren and visual emergency."""
    app_state = request.app.state
    app_state.audio_pipeline.set_demo_override(True, {
        "class": "fire_truck_siren",
        "confidence": 0.94
    })
    app_state.vision_pipeline.set_demo_override(True, {
        "counts": {"car": 3, "motorcycle": 0, "bus": 0, "truck": 1, "ambulance": 1, "total": 5},
        "density": "LOW",
        "ambulance_detected": True,
        "ambulance_confidence": 0.89,
        "ambulance_direction": "EAST",
        "direction_counts": {"NORTH": 1, "SOUTH": 1, "EAST": 3, "WEST": 0}
    })
    return {"status": "success", "scenario": "FIRE_TRUCK_CONFIRMATION", "expected": "Emergency Green Corridor EAST"}

@demo_router.post("/police")
async def demo_police(request: Request):
    """Simulates Police siren and visual emergency."""
    app_state = request.app.state
    app_state.audio_pipeline.set_demo_override(True, {
        "class": "police_siren",
        "confidence": 0.93
    })
    app_state.vision_pipeline.set_demo_override(True, {
        "counts": {"car": 5, "motorcycle": 2, "bus": 0, "truck": 0, "ambulance": 1, "total": 8},
        "density": "MEDIUM",
        "ambulance_detected": True,
        "ambulance_confidence": 0.90,
        "ambulance_direction": "WEST",
        "direction_counts": {"NORTH": 2, "SOUTH": 2, "EAST": 1, "WEST": 3}
    })
    return {"status": "success", "scenario": "POLICE_CONFIRMATION", "expected": "Emergency Green Corridor WEST"}

@demo_router.post("/accident")
async def demo_accident(request: Request):
    """Simulates Case 4: Acoustic Crash/Impact (94%) -> Immediate Safety Hold."""
    app_state = request.app.state
    app_state.audio_pipeline.set_demo_override(True, {
        "class": "accident_impact",
        "confidence": 0.94
    })
    app_state.vision_pipeline.set_demo_override(True, {
        "counts": {"car": 4, "motorcycle": 1, "bus": 0, "truck": 0, "ambulance": 0, "total": 5},
        "density": "LOW",
        "ambulance_detected": False,
        "direction_counts": {"NORTH": 2, "SOUTH": 1, "EAST": 1, "WEST": 1}
    })
    return {"status": "success", "scenario": "ACCIDENT_ALERT", "expected": "Accident Alert & Safe All-RED Hold"}

@demo_router.post("/audio-only")
async def demo_audio_only(request: Request):
    """Simulates Case 2: Siren heard, but no visual ambulance yet (Verification Window)."""
    app_state = request.app.state
    app_state.audio_pipeline.set_demo_override(True, {
        "class": "ambulance_siren",
        "confidence": 0.92
    })
    app_state.vision_pipeline.set_demo_override(False)
    return {"status": "success", "scenario": "AUDIO_ONLY", "expected": "Possible Emergency (Awaiting Video)"}

@demo_router.post("/video-only")
async def demo_video_only(request: Request):
    """Simulates Case 3: Visual ambulance with silent siren."""
    app_state = request.app.state
    app_state.audio_pipeline.set_demo_override(False)
    app_state.vision_pipeline.set_demo_override(True, {
        "counts": {"car": 3, "motorcycle": 1, "bus": 0, "truck": 0, "ambulance": 1, "total": 5},
        "density": "LOW",
        "ambulance_detected": True,
        "ambulance_confidence": 0.88,
        "ambulance_direction": "SOUTH",
        "direction_counts": {"NORTH": 1, "SOUTH": 3, "EAST": 1, "WEST": 0}
    })
    return {"status": "success", "scenario": "VIDEO_ONLY", "expected": "Visual Priority Verification"}

@demo_router.post("/reset")
async def demo_reset(request: Request):
    """Clears all demo overrides and returns cleanly to live sensors."""
    app_state = request.app.state
    app_state.vision_pipeline.set_demo_override(False)
    app_state.audio_pipeline.set_demo_override(False)
    return {"status": "success", "scenario": "RESET", "mode": "LIVE_SENSORS"}
