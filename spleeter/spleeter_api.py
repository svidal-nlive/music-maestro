from fastapi import FastAPI, UploadFile, File, HTTPException
import subprocess
import os
import shutil

app = FastAPI()

# Directories for input and output (should be mounted as shared volumes)
INPUT_DIR = "/input"
OUTPUT_DIR = "/output"

@app.post("/process/")
async def process_audio(file: UploadFile = File(...)):
    file_location = os.path.join(INPUT_DIR, file.filename)
    # Save the uploaded file to the input directory.
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Build the Spleeter command with the input file as a positional argument.
    command = [
        "spleeter", "separate",
        "-o", OUTPUT_DIR,
        "-p", "spleeter:5stems",
        file_location
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Spleeter processing failed: {e}")

    return {"detail": f"Processing complete for {file.filename}"}
