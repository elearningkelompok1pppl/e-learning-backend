from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from main import db

router = APIRouter()

class SoalQuizCreate(BaseModel):
    quiz_id: int
    pertanyaan: str
    pilihan_a: str
    pilihan_b: str
    pilihan_c: str
    pilihan_d: str
    jawaban_benar: str
    bobot: int | None = 1

@router.post("/")
async def create_soal_quiz(data: SoalQuizCreate):
    return await db.soal_quiz.create(data=data.dict())

@router.get("/")
async def get_all_soal():
    return await db.soal_quiz.find_many()

@router.get("/{id}")
async def get_soal(id: int):
    soal = await db.soal_quiz.find_unique(where={"id": id})
    if not soal:
        raise HTTPException(404, "Soal not found")
    return soal

@router.put("/{id}")
async def update_soal(id: int, data: SoalQuizCreate):
    return await db.soal_quiz.update(where={"id": id}, data=data.dict())

@router.delete("/{id}")
async def delete_soal(id: int):
    await db.soal_quiz.delete(where={"id": id})
    return {"message": "Soal deleted"}
