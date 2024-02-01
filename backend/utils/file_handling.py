from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse
from pathlib import Path
from datetime import datetime
import random
import shutil
from typing import Annotated

UPLOAD_DIRECTORY = "./public/images"
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)


async def upload_file(file: bytes, request: Request):
    try:
        filename = Path(file.filename)
        file_extension = filename.suffix
        filename_without_extension = filename.stem.lower().replace(" ", "-")
        unique_filename = f"{filename_without_extension}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(0, 100000)}{file_extension}"

        destination = Path(UPLOAD_DIRECTORY) / unique_filename
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {
            "url": f"{request.base_url}images/{unique_filename}",
            "localPath": str(destination)
        }
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "Error while uploading file"})