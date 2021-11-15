import os
import shutil
import requests

from fastapi import FastAPI, File, Form
from fastapi.datastructures import UploadFile
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from scripts import file_handler, assignment, video, translate

app = FastAPI()


origins = [
    "http://localhost:8080",
    "*"
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


@app.post("/assignment/question/upload")
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


@app.post("/assignment/answer/upload")
def upload_assignment_answer(course_code: str = Form(...), assignment_id: str = Form(...), 
                            file_obj: UploadFile = Form(...), roll_no: str = Form(...)):
    """Upload answer to IBM Cloud Object Storage

    Args:
        course_code (str, optional): Course code of the submitted assignment. Defaults to Form(...).
        assignment_id (str, optional): Assignment ID for which the answer is to be uploaded. Defaults to Form(...).
        file_obj (UploadFile, optional): Word Document(.docx) of the answer. Defaults to Form(...).
        roll_no (str, optional): roll number of the student. Defaults to Form(...).

    Returns:
        str: url of the publically accessible file
    """
    DUMP_DIR = os.path.join(os.getcwd(), 'DUMP')
    FILE_PATH = os.path.join(DUMP_DIR, file_obj.filename)

    with open(FILE_PATH, 'wb+') as f:
        shutil.copyfileobj(file_obj.file, f)

    result_url = file_handler.upload_file(
        "obsidian",
        f"{course_code}/assignment/{assignment_id}/answers/{roll_no}.docx",
        FILE_PATH
    )
    os.remove(FILE_PATH)

    return result_url

class PlagResource(BaseModel):
    course_code: str
    assignment_id: str

@app.post("/assignment/plagiarism")
def check_plag(request_body: PlagResource):
    """Check and return plagiarism scores for all assignments for a given assignment ID

    Args:
        request_body (PlagResource): request body for the request

    Returns:
        dict: One-to-many scores for plagiarism
    """
    course_code = request_body.course_code
    assignment_id = request_body.assignment_id

    assignment.cache_assignments(course_code, assignment_id)
    plag_results = assignment.check_plagiarism()
    return plag_results


class KeywordResource(BaseModel):
    course_code: str
    assignment_id: str
    keywords: list

@app.post("/assignment/keyword")
def check_keywords(request_body: KeywordResource):
    """Check presence of keywords in students assignments

    Args:
        request_body (KeywordResource): request body

    Returns:
        dict: bool list of presence of keywords o
    """
    course_code = request_body.course_code
    assignment_id = request_body.assignment_id
    keywords = request_body.keywords

    assignment.cache_assignments(course_code, assignment_id)
    keyword_results = assignment.keyword_checker(keywords)

    return keyword_results


@app.post("/transcribe")
def transcribe(file_obj: UploadFile = Form(...)):
    """Generates transcription for uploaded video

    Args:
        file_obj (UploadFile, optional): .mp4 video file. Defaults to Form(...).

    Returns:
        dict: transcription of video
    """
    DUMP_DIR = os.path.join(os.getcwd(), 'DUMP')
    FILE_PATH = os.path.join(DUMP_DIR, file_obj.filename)

    with open(FILE_PATH, 'wb+') as f:
        shutil.copyfileobj(file_obj.file, f)

    video.video_to_audio(FILE_PATH)
    result = video.speech_to_text()
    
    return result
    


@app.post('/translate')
def translate_pdf(file_obj: UploadFile = Form(...)):
    DUMP_DIR = os.path.join(os.getcwd(), 'DUMP')
    FILE_PATH = os.path.join(DUMP_DIR, file_obj.filename)

    with open(FILE_PATH, 'wb+') as f:
        shutil.copyfileobj(file_obj.file, f)

    document_status = translate.send_document(FILE_PATH)

    return {"dociment_id": document_status['document_id']}

    #* Check if document is ready
    #* If ready, download from client side


@app.post("/transcribe")
def transcribe(file_obj: UploadFile = Form(...)):
    DUMP_DIR = os.path.join(os.getcwd(), 'DUMP')
    FILE_PATH = os.path.join(DUMP_DIR, file_obj.filename)

    with open(FILE_PATH, 'wb+') as f:
        shutil.copyfileobj(file_obj.file, f)

    video.video_to_audio(FILE_PATH)
    result = video.speech_to_text()
    
    os.remove(FILE_PATH)

    return result


class TranscribeResource(BaseModel):
    dropbox_url: str

@app.post("/transcribe_url")
def transcribe_url(request_body: TranscribeResource):
    dropbox_url = request_body.dropbox_url
    try:
        with requests.get(dropbox_url, stream=True) as r:
            with open("DUMP/video.mp4", 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        print("[LOG Download complete")
    except Exception as e:
        return {"error": "download error"}
    
    DUMP_DIR = os.path.join(os.getcwd(), 'DUMP')
    VID_PATH = os.path.join(DUMP_DIR, 'video.mp4')
    video.video_to_audio(VID_PATH)
    result = video.speech_to_text()
    
    os.remove(VID_PATH)

    return result