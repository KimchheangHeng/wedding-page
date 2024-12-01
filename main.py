from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import asyncio

app = FastAPI()

# Serve the HTML project directory
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# Store WebSocket connections
connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            # Keep the WebSocket connection alive
            await asyncio.sleep(10)
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        connections.remove(websocket)

@app.post("/send-key")
async def send_key(key: str):
    # Broadcast the key to all connected WebSocket clients
    for connection in connections:
        await connection.send_text(key)
    return {"status": "success", "key": key}