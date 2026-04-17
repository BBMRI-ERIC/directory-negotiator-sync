import threading
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/actuator/health")
def health():
    return {"status": "UP"}

def start(port=8088):
    threading.Thread(
        target=lambda: uvicorn.run(app, host="0.0.0.0", port=port, log_level="error"),
        daemon=True
    ).start()