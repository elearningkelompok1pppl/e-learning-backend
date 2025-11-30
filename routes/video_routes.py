# routes/video_routes.py — Manajemen Video Kegiatan (RBAC Protected)
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from core.permissions import authorize_access
from main import db

router = APIRouter(
    tags=["Video Kegiatan"],
    dependencies=[Depends(authorize_access)]  # ✅ Semua endpoint butuh JWT
)

# SCHEMA: Data Video Kegiatan
class VideoCreate(BaseModel):
    judul: str = Field(..., description="Judul video kegiatan")
    deskripsi: str | None = Field(default=None, description="Deskripsi video")
    youtube_url: str = Field(..., description="URL lengkap video YouTube")
    youtube_id: str | None = Field(default=None, description="ID YouTube unik (opsional)")
    kategori: str = Field(default="Kegiatan", description="Kategori video (Kegiatan, Tutorial, dll)")
    jurusan_id: int | None = Field(default=None, description="ID jurusan terkait video")
    thumbnail: str | None = Field(default=None, description="URL thumbnail video")
    uploaded_by: int | None = Field(default=None, description="ID user pengunggah (Admin/Guru)")
    status: str = Field(default="Active", description="Status video (Active / Hidden)")


# CREATE — Tambah Video (Admin & Guru)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_video(data: VideoCreate, user=Depends(authorize_access)):
    role = user.get("role")

    # 🔒 Hanya Admin dan Guru
    if role not in ["Admin", "Guru"]:
        raise HTTPException(status_code=403, detail="❌ Hanya Admin atau Guru yang dapat menambah video")

    # Auto isi uploaded_by jika Guru login
    if role == "Guru" and not data.uploaded_by:
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru:
            raise HTTPException(status_code=404, detail="Guru tidak ditemukan")
        data.uploaded_by = guru.id

    try:
        created = await db.video_kegiatan.create(data=data.dict())
        return {"message": "✅ Video berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat video: {str(e)}")


# READ — Ambil Semua Video (Semua Role)
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_video(user=Depends(authorize_access)):
    role = user.get("role")

    try:
        if role == "Admin":
            video_list = await db.video_kegiatan.find_many(include={"jurusan": True, "admin": True})

        elif role == "Guru":
            guru = await db.guru.find_unique(where={"email": user["sub"]})
            if not guru:
                raise HTTPException(status_code=404, detail="Guru tidak ditemukan")
            video_list = await db.video_kegiatan.find_many(
                where={"uploaded_by": guru.id},
                include={"jurusan": True}
            )

        elif role == "Murid":
            video_list = await db.video_kegiatan.find_many(
                where={"status": "Active"},
                include={"jurusan": True}
            )

        else:
            raise HTTPException(status_code=403, detail="Akses ditolak")

        return {"total": len(video_list), "data": video_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data video: {str(e)}")


# READ — Ambil Video Berdasarkan ID
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_video(id: int, user=Depends(authorize_access)):
    video = await db.video_kegiatan.find_unique(
        where={"id": id},
        include={"jurusan": True, "admin": True}
    )
    if not video:
        raise HTTPException(status_code=404, detail="❌ Video tidak ditemukan")

    # Murid hanya boleh lihat video aktif
    if user.get("role") == "Murid" and video.status != "Active":
        raise HTTPException(status_code=403, detail="❌ Video ini belum dapat diakses")

    return {"data": video}


# UPDATE — Ubah Video (Admin & Guru Pemilik)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_video(id: int, data: VideoCreate, user=Depends(authorize_access)):
    role = user.get("role")
    existing = await db.video_kegiatan.find_unique(where={"id": id})

    if not existing:
        raise HTTPException(status_code=404, detail="❌ Video tidak ditemukan")

    # Guru hanya boleh ubah video miliknya
    if role == "Guru":
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru or existing.uploaded_by != guru.id:
            raise HTTPException(status_code=403, detail="❌ Tidak boleh mengubah video milik guru lain")

    if role not in ["Admin", "Guru"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")

    try:
        updated = await db.video_kegiatan.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Video berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui video: {str(e)}")


# DELETE — Hapus Video (Admin & Guru Pemilik)
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_video(id: int, user=Depends(authorize_access)):
    role = user.get("role")
    existing = await db.video_kegiatan.find_unique(where={"id": id})

    if not existing:
        raise HTTPException(status_code=404, detail="❌ Video tidak ditemukan")

    # Guru hanya boleh hapus video miliknya
    if role == "Guru":
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru or existing.uploaded_by != guru.id:
            raise HTTPException(status_code=403, detail="❌ Tidak boleh menghapus video milik guru lain")

    if role not in ["Admin", "Guru"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")

    try:
        await db.video_kegiatan.delete(where={"id": id})
        return {"message": "🗑️ Video berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus video: {str(e)}")