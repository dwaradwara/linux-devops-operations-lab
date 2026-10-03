from fastapi import FastAPI
import socket

app = FastAPI()

@app.get("/")
def root():
    return {
        "service": "devops-demo-api",
        "status": "running",
        "host": socket.gethostname()
    }

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.get("/api/info")
def info():
    return {
        "application": "Linux DevOps Operations Lab",
        "environment": "test",
        "managed_by": "Ansible"
    }
