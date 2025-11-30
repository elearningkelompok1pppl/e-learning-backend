# routes/soal_quiz_routes.py — Manajemen Soal Quiz (RBAC Protected)
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from core.permissions import authorize_access
from main import db

router = APIRouter(
    tags=["Soal Quiz"],
    dependencies=[Depends(authorize_access)]  # ✅ Semua endpoint butuh JWT
)

# SCHEMA: Data Soal Quiz
class SoalQuizCreate(BaseModel):
    quiz_id: int = Field(..., description="ID dari quiz terkait")
    pertanyaan: str = Field(..., description="Isi pertanyaan quiz")
    pilihan_a: str = Field(..., description="Pilihan A")
    pilihan_b: str = Field(..., description="Pilihan B")
    pilihan_c: str = Field(..., description="Pilihan C")
    pilihan_d: str = Field(..., description="Pilihan D")
    jawaban_benar: str = Field(..., description="Jawaban benar (A/B/C/D)")
    bobot: int | None = Field(default=1, description="Nilai bobot untuk soal")


# CREATE — Tambah Soal Quiz (Admin & Guru Pemilik Quiz)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_soal_quiz(data: SoalQuizCreate, user=Depends(authorize_access)):
    role = user.get("role")

    # 🔒 Hanya Admin dan Guru yang boleh menambah soal
    if role not in ["Admin", "Guru"]:
        raise HTTPException(status_code=403, detail="❌ Hanya Admin atau Guru yang dapat menambah soal")

    # 🧠 Validasi quiz-nya
    quiz = await db.quiz.find_unique(where={"id": data.quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz tidak ditemukan")

    # 🔒 Jika Guru → pastikan quiz miliknya
    if role == "Guru":
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru or quiz.guru_id != guru.id:
            raise HTTPException(status_code=403, detail="❌ Tidak bisa menambah soal pada quiz milik guru lain")

    try:
        created = await db.soal_quiz.create(data=data.dict())
        return {"message": "✅ Soal quiz berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat soal quiz: {str(e)}")


# READ — Ambil Semua Soal (Admin & Guru Pemilik)
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_soal(user=Depends(authorize_access)):
    role = user.get("role")

    try:
        if role == "Admin":
            soal_list = await db.soal_quiz.find_many(include={"quiz": True})

        elif role == "Guru":
            guru = await db.guru.find_unique(where={"email": user["sub"]})
            if not guru:
                raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

            soal_list = await db.soal_quiz.find_many(
                where={"quiz": {"guru_id": guru.id}},
                include={"quiz": True}
            )

        elif role == "Murid":
            # Murid hanya bisa lihat soal dari quiz yang aktif (status != Draft)
            soal_list = await db.soal_quiz.find_many(
                where={"quiz": {"status": {"not": "Draft"}}},
                include={"quiz": True}
            )
        else:
            raise HTTPException(status_code=403, detail="Akses ditolak")

        return {"total": len(soal_list), "data": soal_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil soal: {str(e)}")


# READ — Ambil Soal Berdasarkan ID (Semua Role)
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_soal(id: int, user=Depends(authorize_access)):
    soal = await db.soal_quiz.find_unique(
        where={"id": id},
        include={"quiz": True}
    )

    if not soal:
        raise HTTPException(status_code=404, detail="❌ Soal tidak ditemukan")

    # Jika Murid → hanya boleh lihat soal quiz yang aktif
    if user.get("role") == "Murid" and soal.quiz.status == "Draft":
        raise HTTPException(status_code=403, detail="❌ Soal ini belum dapat diakses (quiz belum aktif)")

    return {"data": soal}


# UPDATE — Ubah Soal (Admin & Guru Pemilik Quiz)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_soal(id: int, data: SoalQuizCreate, user=Depends(authorize_access)):
    role = user.get("role")
    existing = await db.soal_quiz.find_unique(
        where={"id": id},
        include={"quiz": True}
    )

    if not existing:
        raise HTTPException(status_code=404, detail="❌ Soal tidak ditemukan")

    #  Hanya Admin atau Guru pemilik quiz yang boleh ubah
    if role == "Guru":
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru or existing.quiz.guru_id != guru.id:
            raise HTTPException(status_code=403, detail="❌ Tidak boleh mengubah soal milik guru lain")

    if role not in ["Admin", "Guru"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")

    try:
        updated = await db.soal_quiz.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Soal quiz berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui soal: {str(e)}")


# DELETE — Hapus Soal (Admin & Guru Pemilik Quiz)
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_soal(id: int, user=Depends(authorize_access)):
    role = user.get("role")
    existing = await db.soal_quiz.find_unique(
        where={"id": id},
        include={"quiz": True}
    )

    if not existing:
        raise HTTPException(status_code=404, detail="❌ Soal tidak ditemukan")

    # 🔒 Hanya Admin atau Guru pemilik quiz
    if role == "Guru":
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru or existing.quiz.guru_id != guru.id:
            raise HTTPException(status_code=403, detail="❌ Tidak boleh menghapus soal milik guru lain")

    if role not in ["Admin", "Guru"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")

    try:
        await db.soal_quiz.delete(where={"id": id})
        return {"message": "🗑️ Soal quiz berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus soal: {str(e)}")