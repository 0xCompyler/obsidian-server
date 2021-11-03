import os
import shutil

from logging import debug
from typing import Optional
from fastapi import FastAPI, File, Form
from fastapi.datastructures import UploadFile
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from scripts import file_handler

app = FastAPI()


origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    


@app.post("/CreateCourse")
def create_course(course_code: str = Form(...), file_obj: UploadFile = Form(...)):
    """Create a new course

    Args:
        course_code (str, optional): Course code of the new code. Defaults to Form(...).
        file (UploadFile, optional): Course handout of the new course. Defaults to Form(...).

    Returns:
        str: URL of the uploaded course handout
    """
    #* save the file in DUMP/
    #* create a new directory in the obsidian bucket
    #* place a pdf with the name as course code.pdf
    #* delete the file in DUMP
    #* return URL of the uploaded course handout

    DUMP_DIR = os.path.join(os.getcwd(), 'DUMP')
    FILE_PATH = os.path.join(DUMP_DIR, file_obj.filename)

    with open(FILE_PATH, 'wb+') as f:
        shutil.copyfileobj(file_obj.file, f)
    
    result_url = file_handler.upload_file("obsidian", f"{course_code}/{course_code}.pdf", FILE_PATH)
    os.remove(FILE_PATH)

    return result_url


@app.post("/assignment/question")
def upload_question(course_code: str = Form(...), assignment_id: str = Form(...), file_obj: UploadFile = Form(...)):
    """Create and upload an assignment

    Args:
        course_code (str, optional): Course Code of the assignment. Defaults to Form(...).
        assignment_id (str, optional): Assignment number. Defaults to Form(...).
        file_obj (UploadFile, optional): Question paper of the assignment. Defaults to Form(...).

    Returns:
        str: URL of the question paper
    """
    DUMP_DIR = os.path.join(os.getcwd(), 'DUMP')
    FILE_PATH = os.path.join(DUMP_DIR, file_obj.filename)

    with open(FILE_PATH, 'wb+') as f:
        shutil.copyfileobj(file_obj.file, f)

    result_url = file_handler.upload_file(
        "obsidian",
        f"{course_code}/assignment/{assignment_id}/{assignment_id}.pdf",
        FILE_PATH
    )
    os.remove(FILE_PATH)

    return result_url


@app.post("assignment/answer/upload")
def upload_assignment_answer(course_code: str = Form(...), assignment_id: str = Form(...), 
                            file_obj: UploadFile = Form(...), roll_no: str = Form(...)):
    DUMP_DIR = os.path.join(os.getcwd(), 'DUMP')
    FILE_PATH = os.path.join(DUMP_DIR, file_obj.filename)

    with open(FILE_PATH, 'wb+') as f:
        shutil.copyfileobj(file_obj.file, f)

    result_url = file_handler.upload_file(
        "obsidian",
        f"{course_code}/assignment/{assignment_id}/answers/{roll_no}.pdf",
        FILE_PATH
    )
    os.remove(FILE_PATH)

    return result_url
