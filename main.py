import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

try:
    import RPi.GPIO as GPIO  # Only import if running on Raspberry Pi

    IS_RASPBERRY_PI = True
except ImportError:
    IS_RASPBERRY_PI = False

# GPIO setup (if running on Raspberry Pi)
BUTTON_PIN_A = 18  # GPIO pin number for Button A
BUTTON_PIN_B = 23  # GPIO pin number for Button B

if IS_RASPBERRY_PI:
    GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
    GPIO.setup(BUTTON_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUTTON_PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Starting application...")
    await some_startup_task()  # Example: Initialize database or other services
    yield  # This separates startup and shutdown
    # Shutdown logic
    print("Shutting down application...")
    await some_shutdown_task()  # Example: Cleanup resources


app = FastAPI(lifespan=lifespan)


# Example Task Functions
async def some_startup_task():
    print("Running startup tasks...")
    if IS_RASPBERRY_PI:
        print("Starting button listener...")
        asyncio.create_task(button_listener())


async def some_shutdown_task():
    print("Running shutdown tasks...")
    if IS_RASPBERRY_PI:
        GPIO.cleanup()  # Clean up GPIO resources


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
            for connection in connections:
                await connection.send_text(message)
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


@app.get("/test")
async def get_html():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WebSocket Test</title>
        <script>
            let ws;

            function initWebSocket() {
                ws = new WebSocket("ws://localhost:8000/ws");
                ws.onopen = () => console.log("WebSocket connection established");
                ws.onmessage = (event) => console.log("Message from server:", event.data);
                ws.onerror = (error) => console.error("WebSocket error:", error);
                ws.onclose = () => console.warn("WebSocket connection closed");
            }

            function sendMessage(message) {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(message);
                    console.log(`Sent: ${message}`);
                } else {
                    console.error("WebSocket is not open.");
                }
            }

            window.onload = initWebSocket;
        </script>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <button onclick="sendMessage('a')">Send "a"</button>
        <button onclick="sendMessage('b')">Send "b"</button>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


# Serve static files
app.mount("/", StaticFiles(directory=".", html=True))


# Function to handle GPIO button presses
async def button_listener():
    if not IS_RASPBERRY_PI:
        print("GPIO button listener is not available on non-Raspberry Pi systems.")
        return

    while True:
        if GPIO.input(BUTTON_PIN_A) == GPIO.HIGH:  # Button A is pressed
            print("Button A pressed")
            await send_message_to_all_clients("a")
            await asyncio.sleep(0.3)  # Debounce delay

        if GPIO.input(BUTTON_PIN_B) == GPIO.HIGH:  # Button B is pressed
            print("Button B pressed")
            await send_message_to_all_clients("b")
            await asyncio.sleep(0.3)  # Debounce delay

        await asyncio.sleep(0.1)  # Short delay to avoid CPU overuse
