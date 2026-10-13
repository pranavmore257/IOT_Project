import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.config.settings import CONFIG
from backend.database.database import init_db
from backend.vision.inference import VisionPipeline
from backend.audio.inference import AudioPipeline
from backend.decision.decision_engine import MultimodalDecisionEngine
from backend.communication.mqtt_client import MQTTTrafficClient
from backend.communication.esp32_controller import ESP32Controller
from backend.api.routes import api_router
from backend.api.demo_routes import demo_router
from backend.api.websocket import ws_manager

# Background tick task
tick_task = None

async def system_tick_loop(app: FastAPI):
    """10 Hz central loop orchestrating AI sensors, decision engine, IoT and WebSockets."""
    app_state = app.state
    while True:
        try:
            # 1. Fetch latest sensory outputs
            v_res = app_state.vision_pipeline.get_latest_result()
            a_res = app_state.audio_pipeline.get_latest_result()

            # 2. Process via Multimodal Decision Engine
            decision_res = app_state.decision_engine.process(a_res, v_res)
            app_state.latest_decision = decision_res

            # 3. Dispatch to ESP32 over MQTT
            sig_state = decision_res.get("signal_state", {})
            mode = decision_res.get("mode", "NORMAL")
            priority = decision_res.get("priority", "LOW")
            app_state.esp32_controller.dispatch_signal_state(sig_state, mode, priority)

            # 4. Broadcast unified state via WebSockets
            esp_status = app_state.esp32_controller.get_status()
            broadcast_payload = {
                "timestamp": time.time(),
                "video": v_res,
                "audio": a_res,
                "decision": decision_res,
                "signals": sig_state,
                "system": {
                    "uptime": round(time.time() - app_state.start_time, 1),
                    "camera_connected": v_res.get("is_camera_connected", False),
                    "microphone_connected": a_res.get("is_microphone_connected", False),
                    "esp32_connected": esp_status.get("esp32_connected", False),
                    "mqtt_connected": esp_status.get("mqtt_connected", False),
                    "control_mode": esp_status.get("control_mode", "SIMULATION MODE"),
                    "demo_mode": v_res.get("demo_override", False) or a_res.get("demo_override", False)
                }
            }
            await ws_manager.broadcast(broadcast_payload)
        except Exception as e:
            print(f"[SystemTick] Error in tick loop: {e}")

        await asyncio.sleep(0.1)  # 100ms interval (10 Hz)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tick_task
    print("[Server] Initializing Smart Acoustic & Vision Traffic Signal Backend...")

    # Initialize Database
    init_db()

    # Instantiate subsystems
    app.state.start_time = time.time()
    app.state.vision_pipeline = VisionPipeline()
    app.state.audio_pipeline = AudioPipeline()
    app.state.decision_engine = MultimodalDecisionEngine()

    mqtt_cfg = CONFIG.get("mqtt", {})
    app.state.mqtt_client = MQTTTrafficClient(mqtt_cfg)
    app.state.esp32_controller = ESP32Controller(app.state.mqtt_client)

    app.state.latest_decision = {
        "mode": "NORMAL",
        "priority": "LOW",
        "emergency_score": 0.0,
        "target_direction": "NONE",
        "reason": "Initializing...",
        "signal_state": {
            "state": "NS_GREEN",
            "signals": {"NORTH": "GREEN", "SOUTH": "GREEN", "EAST": "RED", "WEST": "RED"},
            "remaining_seconds": 10
        }
    }

    # Start workers
    app.state.vision_pipeline.start()
    app.state.audio_pipeline.start()
    app.state.mqtt_client.start()

    # Start tick loop
    tick_task = asyncio.create_task(system_tick_loop(app))
    print("[Server] Subsystems started successfully.")

    yield

    # Shutdown
    print("[Server] Shutting down subsystems...")
    if tick_task:
        tick_task.cancel()
    app.state.vision_pipeline.stop()
    app.state.audio_pipeline.stop()
    app.state.mqtt_client.stop()
    print("[Server] Clean shutdown complete.")

app = FastAPI(
    title="Smart Acoustic & Vision Traffic Signal API",
    description="Multimodal AI + ESP32 IoT Traffic Management Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(api_router)
app.include_router(demo_router)

# Mount frontend build if dist exists
dist_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        return {
            "project": "Smart Acoustic & Vision Traffic Signal",
            "version": "1.0.0",
            "status": "ONLINE",
            "docs": "/docs",
            "api": "/api/status",
            "note": "Frontend running on Vite dev server or static build pending."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
