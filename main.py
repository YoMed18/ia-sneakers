import json
from http.client import HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

import scrap.scrap as sp
from fastapi import FastAPI, UploadFile, File

from model.predict import predict_image

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScrapRequest(BaseModel):
    url: str
    folder_name: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/scrap/")
async def scrap(request_data: ScrapRequest):
    try:
        sp.telecharger_toutes_images(request_data.url, request_data.folder_name)
        return {"message": "Images have been successfully downloaded."}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {str(e)}")


@app.post("/predict/")
async def predict(image: UploadFile = File(...)):
    content = await image.read()
    print(f"Reçu {image.filename}, taille {len(content)} bytes")
    detected_objects = predict_image(content)

    return JSONResponse(content={"detected_objects": detected_objects})
