# Creates the FastAPI app, registers the feature routers and exception handlers, and serves as the application entry point.
from fastapi import FastAPI

app=FastAPI()

@app.get("/")
async def root():
    return {"message": "api"}