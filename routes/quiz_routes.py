# routes/quiz_routes.py — Manajemen Quiz (RBAC Protected)

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime
from core.permissions import authorize_access
from main import db

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"],
    dependencies=[Depends(authorize_access)]  # ✅ Semua endpoint butuh JWT
)

# SCHEMA: Data Quiz
class QuizCreate(BaseModel):
    judul: str = Field(..., description="Judul quiz")
    deskripsi: str | None = Field(default=None, description="Deskripsi quiz")
    mata_pelajaran_id: int | None = Field(default=None, description="ID mata pelajaran")
    kelas_id: int | None = Field(default=None, description="ID kelas")
    guru_id: int | None = Field(default=None, description="ID guru pembuat quiz")
    durasi: int | None = Field(default=None, description="Durasi quiz (menit)")
    tanggal_mulai: datetime | None = Field(default=None, description="Tanggal mulai quiz")
    tanggal_selesai: datetime | None = Field(default=None, description="Tanggal berakhir quiz")
    status: str | None = Field(default="Draft", description="Status quiz: Draft / Aktif / Selesai")


# CREATE — Tambah Quiz (Admin & Guru)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_quiz(data: QuizCreate, user=Depends(authorize_access)):
    role = user.get("role")

    # ✅ Hanya Admin atau Guru
    if role not in ["Admin", "Guru"]:
        raise HTTPException(status_code=403, detail="❌ Hanya Admin atau Guru yang bisa membuat quiz")

    # Jika Guru → otomatis isi guru_id berdasarkan akun login
    if role == "Guru" and not data.guru_id:
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru:
            raise HTTPException(status_code=404, detail="Guru tidak ditemukan")
        data.guru_id = guru.id

    try:
        created = await db.quiz.create(data=data.dict())
        return {"message": "✅ Quiz berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat quiz: {str(e)}")


# READ — Ambil Semua Quiz (Admin, Guru, Murid)
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_quiz(user=Depends(authorize_access)):
    role = user.get("role")

    try:
        if role == "Admin":
            quiz_list = await db.quiz.find_many(include={"mata_pelajaran": True, "kelas": True, "guru": True})

        elif role == "Guru":
            guru = await db.guru.find_unique(where={"email": user["sub"]})
            if not guru:
                raise HTTPException(status_code=404, detail="Guru tidak ditemukan")
            quiz_list = await db.quiz.find_many(
                where={"guru_id": guru.id},
                include={"mata_pelajaran": True, "kelas": True}
            )

        elif role == "Murid":
            murid = await db.murid.find_unique(
                where={"email": user["sub"]},
                include={"kelas": True}
            )
            if not murid:
                raise HTTPException(status_code=404, detail="Murid tidak ditemukan")

            quiz_list = await db.quiz.find_many(
                where={"kelas_id": murid.kelas_id},
                include={"mata_pelajaran": True, "guru": True}
            )

        else:
            raise HTTPException(status_code=403, detail="Akses ditolak")

        return {"total": len(quiz_list), "data": quiz_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil quiz: {str(e)}")


# READ — Ambil Quiz Berdasarkan ID (Semua Role)
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_quiz(id: int, user=Depends(authorize_access)):
    quiz = await db.quiz.find_unique(
        where={"id": id},
        include={"guru": True, "mata_pelajaran": True, "kelas": True}
    )
    if not quiz:
        raise HTTPException(status_code=404, detail="❌ Quiz tidak ditemukan")
    return {"data": quiz}


# UPDATE — Ubah Quiz (Admin & Guru Pemilik)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_quiz(id: int, data: QuizCreate, user=Depends(authorize_access)):
    role = user.get("role")
    existing = await db.quiz.find_unique(where={"id": id})

    if not existing:
        raise HTTPException(status_code=404, detail="❌ Quiz tidak ditemukan")

    # Guru hanya boleh ubah quiz miliknya
    if role == "Guru":
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru or existing.guru_id != guru.id:
            raise HTTPException(status_code=403, detail="❌ Tidak bisa mengubah quiz milik guru lain")

    if role not in ["Admin", "Guru"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")

    try:
        updated = await db.quiz.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Quiz berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui quiz: {str(e)}")


# DELETE — Hapus Quiz (Admin & Guru Pemilik)
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_quiz(id: int, user=Depends(authorize_access)):
    role = user.get("role")
    existing = await db.quiz.find_unique(where={"id": id})

    if not existing:
        raise HTTPException(status_code=404, detail="❌ Quiz tidak ditemukan")

    # Guru hanya boleh hapus quiz miliknya
    if role == "Guru":
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru or existing.guru_id != guru.id:
            raise HTTPException(status_code=403, detail="❌ Tidak bisa menghapus quiz milik guru lain")

    if role not in ["Admin", "Guru"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")

    try:
        await db.quiz.delete(where={"id": id})
        return {"message": "🗑️ Quiz berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus quiz: {str(e)}")
