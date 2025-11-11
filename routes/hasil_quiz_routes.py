# routes/hasil_quiz_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from main import db

router = APIRouter()


# ===============================================================
# 📘 Model Input untuk Hasil Quiz
# ===============================================================
class HasilQuizCreate(BaseModel):
    murid_id: int | None = None
    quiz_id: int | None = None
    mata_pelajaran_id: int | None = None
    score: float | None = None
    total_soal: int | None = None
    jawaban_benar: int | None = None
    waktu_mulai: str | None = None
    waktu_selesai: str | None = None


# ===============================================================
# 🧩 CREATE - Tambah Data Hasil Quiz
# ===============================================================
@router.post("/")
async def create_hasil_quiz(data: HasilQuizCreate):
    try:
        created = await db.hasil_quiz.create(data=data.dict())
        return {"message": "✅ Hasil quiz berhasil ditambahkan", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===============================================================
# 📜 READ - Ambil Semua Data
# ===============================================================
@router.get("/")
async def get_all_hasil_quiz():
    try:
        hasil = await db.hasil_quiz.find_many()
        return {"total": len(hasil), "data": hasil}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===============================================================
# 🔍 READ - Ambil Berdasarkan ID
# ===============================================================
@router.get("/{id}")
async def get_hasil_quiz(id: int):
    try:
        hasil = await db.hasil_quiz.find_unique(where={"id": id})
        if not hasil:
            raise HTTPException(status_code=404, detail="❌ Hasil quiz tidak ditemukan")
        return hasil
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===============================================================
# ✏️ UPDATE - Ubah Data Berdasarkan ID
# ===============================================================
@router.put("/{id}")
async def update_hasil_quiz(id: int, data: HasilQuizCreate):
    try:
        updated = await db.hasil_quiz.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Hasil quiz berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===============================================================
# ❌ DELETE - Hapus Data Berdasarkan ID
# ===============================================================
@router.delete("/{id}")
async def delete_hasil_quiz(id: int):
    try:
        await db.hasil_quiz.delete(where={"id": id})
        return {"message": "🗑️ Hasil quiz berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
