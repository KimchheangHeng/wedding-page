import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse



app = FastAPI()

def is_raspberry_pi():
    try:
        with open("/etc/os-release") as f:
            os_info = f.read().lower()
        return "raspbian" in os_info or "raspberry pi" in os_info
    except FileNotFoundError:
        return False
    
if is_raspberry_pi():
    import RPi.GPIO as GPIO # type: ignore
    # GPIO Setup for button press (e.g., using GPIO pin 18)
    BUTTON_PIN = 18  # Replace with your correct GPIO pin number
    GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set up the button pin

# # Serve the HTML project directory
# app.mount("/", StaticFiles(directory=".", html=True), name="static")

# Serve the HTML page with WebSocket connection
@app.get("/test")
async def get():
    html = """
    <html>
        <head>
            <title>WebSocket and GPIO Button Test</title>
        </head>
        <body>
            <h1>WebSocket and GPIO Button Test</h1>
            <button onclick="sendMessage()">Send Message</button>
            <script>
                let ws = new WebSocket("ws://localhost:8000/ws");

                ws.onopen = function(event) {
                    console.log("WebSocket is connected!");
                };

                ws.onmessage = function(event) {
                    console.log("Message from server:", event.data);
                };

                ws.onclose = function(event) {
                    console.log("WebSocket is closed.");
                };

                ws.onerror = function(error) {
                    console.log("WebSocket error:", error);
                };

                function sendMessage() {
                    ws.send("Button was clicked from HTML!");
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html)

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
            await websocket.send_text("a")

            # Check if the GPIO button is pressed
            # if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Assuming LOW means button is pressed
                # await websocket.send_text("Button Pressed! From Raspberry Pi.")
                # await asyncio.sleep(1)  # Prevent multiple messages in quick succession
    except WebSocketDisconnect:
        print("Client disconnected")
        await websocket.close()


# Shutdown function to clean up GPIO settings when the FastAPI server shuts down
# @app.on_event("shutdown")
# def shutdown_event():
#     if is_raspberry_pi():
#         GPIO.cleanup()
#         print("GPIO cleaned up on shutdown")
