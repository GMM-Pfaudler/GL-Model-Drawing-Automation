import os
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from api.controllers.controller import router as route
import uvicorn
# Run server: fastapi dev main.py
# Debug server: python main.py
# Flow:- Start (Front-End): api/v1 -> reactor_controller.py -> /start -> assembly_service.py -> assembly_repository.py -> Top 3 .iam files
# Flow:- Draw (Fron-End): api/v1 -> reactor_controller.py -> /draw -> assembly_service.py -> part_service -> part_xyz_serv.py -> assembly_repository.py -> part_repository -> part_xyz_repo.py -> inventor_service.py
# Flow:- Open (Front-End): api/v1 -> reactor_controller.py -> /open -> assembly_service.py -> inventor_service.py
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://localhost:9000/", "https://127.0.0.1", "http://10.100.11.179", "http://10.100.13.31", "http://10.100.10.223"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Register the item router with the app
app.include_router(route, prefix="/api/v1", tags=["reactors"])

# app.mount("/", StaticFiles(directory="gl-reactor-rest/static"), name="static")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

@app.get("/")
def serve_vue_root():
    # return "running"
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)