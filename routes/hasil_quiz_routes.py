# routes/hasil_quiz_routes.py — Manajemen Hasil Quiz (RBAC Protected)

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from core.permissions import authorize_access
from core.security import get_current_user
from main import db

router = APIRouter(
    prefix="/hasil-quiz",
    tags=["Hasil Quiz"],
    dependencies=[Depends(authorize_access)]  # ✅ RBAC otomatis
)

# SCHEMA: Model Input untuk Hasil Quiz
class HasilQuizCreate(BaseModel):
    murid_id: int | None = Field(default=None, description="ID Murid yang mengerjakan quiz")
    quiz_id: int | None = Field(default=None, description="ID Quiz yang dikerjakan")
    mata_pelajaran_id: int | None = Field(default=None, description="ID Mata Pelajaran terkait")
    score: float | None = Field(default=None, description="Nilai total yang diperoleh")
    total_soal: int | None = Field(default=None, description="Jumlah soal dalam quiz")
    jawaban_benar: int | None = Field(default=None, description="Jumlah jawaban benar")
    waktu_mulai: str | None = Field(default=None, description="Waktu mulai quiz")
    waktu_selesai: str | None = Field(default=None, description="Waktu selesai quiz")

# CREATE — Tambah Data Hasil Quiz
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_hasil_quiz(data: HasilQuizCreate, current_user: dict = Depends(get_current_user)):
    try:
        role = current_user["role"]
        email = current_user["sub"]

        # Cegah murid menambahkan hasil untuk murid lain
        if role == "Murid":
            murid = await db.murid.find_unique(where={"email": email})
            if not murid:
                raise HTTPException(status_code=404, detail="Murid tidak ditemukan")
            data.murid_id = murid.id

        created = await db.hasil_quiz.create(data=data.dict())
        return {"message": "✅ Hasil quiz berhasil ditambahkan", "data": created}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menambahkan hasil quiz: {str(e)}")

# READ — Ambil Semua Data Hasil Quiz
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_hasil_quiz(current_user: dict = Depends(get_current_user)):
    try:
        role = current_user["role"]
        email = current_user["sub"]

        if role == "Admin" or role == "Guru":
            hasil = await db.hasil_quiz.find_many(
                include={"murid": True, "mata_pelajaran": True}
            )
        else:
            murid = await db.murid.find_unique(where={"email": email})
            if not murid:
                raise HTTPException(status_code=404, detail="Murid tidak ditemukan")
            hasil = await db.hasil_quiz.find_many(
                where={"murid_id": murid.id},
                include={"mata_pelajaran": True}
            )

        return {"total": len(hasil), "data": hasil}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data hasil quiz: {str(e)}")

# READ — Ambil Berdasarkan ID
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_hasil_quiz_by_id(id: int, current_user: dict = Depends(get_current_user)):
    try:
        role = current_user["role"]
        email = current_user["sub"]

        hasil = await db.hasil_quiz.find_unique(
            where={"id": id},
            include={"murid": True, "mata_pelajaran": True}
        )

        if not hasil:
            raise HTTPException(status_code=404, detail="❌ Hasil quiz tidak ditemukan")

        if role == "Murid":
            murid = await db.murid.find_unique(where={"email": email})
            if hasil.murid_id != murid.id:
                raise HTTPException(status_code=403, detail="Kamu tidak boleh melihat hasil quiz milik murid lain")

        return {"data": hasil}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil hasil quiz: {str(e)}")

# UPDATE — Ubah Data Hasil Quiz (Admin & Guru Only)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_hasil_quiz(id: int, data: HasilQuizCreate, current_user: dict = Depends(get_current_user)):
    role = current_user["role"]
    if role == "Murid":
        raise HTTPException(status_code=403, detail="Murid tidak boleh mengedit hasil quiz")

    existing = await db.hasil_quiz.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Hasil quiz tidak ditemukan")

    try:
        updated = await db.hasil_quiz.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Hasil quiz berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui hasil quiz: {str(e)}")

# DELETE — Hapus Data (Admin Only)
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_hasil_quiz(id: int, current_user: dict = Depends(get_current_user)):
    role = current_user["role"]
    if role != "Admin":
        raise HTTPException(status_code=403, detail="Hanya Admin yang boleh menghapus hasil quiz")

    try:
        existing = await db.hasil_quiz.find_unique(where={"id": id})
        if not existing:
            raise HTTPException(status_code=404, detail="Hasil quiz tidak ditemukan")

        await db.hasil_quiz.delete(where={"id": id})
        return {"message": "🗑️ Hasil quiz berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus hasil quiz: {str(e)}")
