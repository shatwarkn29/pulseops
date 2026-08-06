from fastapi import FastAPI

app = FastAPI(
    title="PulseOps API",
    description="Entriprise Website Monitoring Platform",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "application": "PulseOps API",
        "status":"Running"
    }
