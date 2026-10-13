import asyncio
import time
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

from backend.api.websocket import ws_manager
from backend.database.database import get_recent_events, clear_events

api_router = APIRouter(prefix="/api", tags=["Traffic System API"])

class ManualSignalRequest(BaseModel):
    north: str = "GREEN"
    south: str = "GREEN"
    east: str = "RED"
    west: str = "RED"

@api_router.get("/status")
async def get_system_status(request: Request):
    app_state = request.app.state
    v_res = app_state.vision_pipeline.get_latest_result()
    a_res = app_state.audio_pipeline.get_latest_result()
    esp_res = app_state.esp32_controller.get_status()

    return {
        "system": {
            "name": "Smart Acoustic & Vision Traffic Signal",
            "status": "ONLINE",
            "uptime_seconds": round(time.time() - app_state.start_time, 1)
        },
        "webcam": {
            "connected": v_res.get("is_camera_connected", False),
            "status": "CONNECTED" if v_res.get("is_camera_connected") else "SIMULATED / VIRTUAL",
            "fps": v_res.get("fps", 0.0),
            "model": "YOLOv8n"
        },
        "microphone": {
            "connected": a_res.get("is_microphone_connected", False),
            "status": "CONNECTED" if a_res.get("is_microphone_connected") else "SIMULATED / SYNTHETIC",
            "model": a_res.get("inference_mode", "HEURISTIC_BASELINE")
        },
        "esp32": {
            "connected": esp_res.get("esp32_connected", False),
            "status": "CONNECTED" if esp_res.get("esp32_connected") else "DISCONNECTED",
            "control_mode": esp_res.get("control_mode", "SIMULATION MODE")
        },
        "mqtt": {
            "connected": esp_res.get("mqtt_connected", False),
            "status": "CONNECTED" if esp_res.get("mqtt_connected") else "OFFLINE (SIMULATION)",
            "broker": esp_res.get("broker")
        },
        "demo_mode": v_res.get("demo_override", False) or a_res.get("demo_override", False)
    }

@api_router.get("/video/status")
async def get_video_status(request: Request):
    app_state = request.app.state
    return app_state.vision_pipeline.get_latest_result()

@api_router.get("/video/feed")
async def get_video_feed(request: Request):
    """Streams the processed live camera feed with YOLO bounding boxes as an MJPEG stream."""
    app_state = request.app.state

    def frame_generator():
        while True:
            frame_bytes = app_state.vision_pipeline.get_latest_jpeg()
            if frame_bytes is not None:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
            time.sleep(0.04)  # ~25 FPS stream

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@api_router.get("/audio/status")
async def get_audio_status(request: Request):
    app_state = request.app.state
    return app_state.audio_pipeline.get_latest_result()

@api_router.get("/traffic")
async def get_traffic_density(request: Request):
    app_state = request.app.state
    v_res = app_state.vision_pipeline.get_latest_result()
    return {
        "vehicle_count": v_res.get("vehicle_count", 0),
        "counts": v_res.get("counts", {}),
        "density": v_res.get("density", "LOW"),
        "direction_counts": v_res.get("direction_counts", {})
    }

@api_router.get("/decision")
async def get_decision(request: Request):
    app_state = request.app.state
    return app_state.latest_decision

@api_router.get("/signals")
async def get_signals(request: Request):
    app_state = request.app.state
    sig = app_state.latest_decision.get("signal_state", {})
    return sig

@api_router.get("/events")
async def get_events(limit: int = Query(50, ge=1, le=200)):
    """Fetches recent traffic history from the SQLite database."""
    events = get_recent_events(limit)
    return {"count": len(events), "events": events}

@api_router.post("/events/clear")
async def clear_event_log():
    clear_events()
    return {"status": "success", "message": "Database event log cleared"}

@api_router.post("/signal/manual")
async def manual_signal(req: ManualSignalRequest, request: Request):
    app_state = request.app.state
    app_state.decision_engine.signal_ctrl.set_manual_signal(
        req.north, req.south, req.east, req.west
    )
    return {"status": "success", "manual_state": req.dict()}

@api_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive client listener
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
