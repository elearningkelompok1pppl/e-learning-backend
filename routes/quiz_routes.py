from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from main import db

router = APIRouter()

class QuizCreate(BaseModel):
    judul: str
    deskripsi: str | None = None
    mata_pelajaran_id: int | None = None
    kelas_id: int | None = None
    guru_id: int | None = None
    durasi: int | None = None
    tanggal_mulai: str | None = None
    tanggal_selesai: str | None = None
    status: str | None = "Draft"

@router.post("/")
async def create_quiz(data: QuizCreate):
    return await db.quiz.create(data=data.dict())

@router.get("/")
async def get_all_quiz():
    return await db.quiz.find_many()

@router.get("/{id}")
async def get_quiz(id: int):
    quiz = await db.quiz.find_unique(where={"id": id})
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    return quiz

@router.put("/{id}")
async def update_quiz(id: int, data: QuizCreate):
    return await db.quiz.update(where={"id": id}, data=data.dict())

@router.delete("/{id}")
async def delete_quiz(id: int):
    await db.quiz.delete(where={"id": id})
    return {"message": "Quiz deleted"}
