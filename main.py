import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

try:
    import RPi.GPIO as GPIO  # Only import if running on Raspberry Pi

    IS_RASPBERRY_PI = True
except ImportError:
    IS_RASPBERRY_PI = False

# GPIO setup (if running on Raspberry Pi)
BUTTON_PIN = 18  # GPIO pin number for the button
if IS_RASPBERRY_PI:
    GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up resistor

# Initialize FastAPI app
app = FastAPI()

# WebSocket endpoint to handle WebSocket connections
connections = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            # Handle message from the client (HTML page)
            message = await websocket.receive_text()
            print(f"Received message from client: {message}")
            await websocket.send_text(f"Message received: {message}")

            # Check if the GPIO button is pressed
            if (
                IS_RASPBERRY_PI and GPIO.input(BUTTON_PIN) == GPIO.LOW
            ):  # Assuming LOW means button is pressed
                await websocket.send_text("Button Pressed! From Raspberry Pi.")
                await asyncio.sleep(1)  # Prevent multiple messages in quick succession
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        await websocket.close()


# New GET method to send query string to all connected WebSocket clients
@app.get("/send_message")
async def send_message_to_all_clients(message: str):
    """
    GET method that takes a query string 'message' and sends it to all connected WebSocket clients.
    """
    try:
        for websocket in connections:
            await websocket.send_text(message)
    except Exception as e:
        print("Error while sending message to WebSocket clients:", e)
    return {
        "message": "Message sent to all WebSocket clients",
        "content": message,
    }


# Serve static files
app.mount("/", StaticFiles(directory=".", html=True))


# GPIO button monitoring task
async def monitor_button():
    if not IS_RASPBERRY_PI:
        print("GPIO monitoring is disabled (not running on Raspberry Pi).")
        return

    print("Starting GPIO button monitoring...")
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Button pressed
            print("Button pressed!")
            for websocket in connections:
                await websocket.send_text("Button was pressed on Raspberry Pi!")
            await asyncio.sleep(0.5)  # Debounce to prevent rapid firing
        await asyncio.sleep(0.1)  # Polling interval


# Run button monitoring in the background
@app.on_event("startup")
async def startup_event():
    if IS_RASPBERRY_PI:
        asyncio.create_task(monitor_button())
