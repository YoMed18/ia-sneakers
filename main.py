import json
from http.client import HTTPException
from pydantic import BaseModel
import scrap.scrap as sp
from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")


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
