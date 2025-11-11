from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from main import db

router = APIRouter()

class VideoCreate(BaseModel):
    judul: str
    deskripsi: str | None = None
    youtube_url: str
    youtube_id: str | None = None
    kategori: str = "Kegiatan"
    jurusan_id: int | None = None
    thumbnail: str | None = None
    uploaded_by: int | None = None
    status: str = "Active"


@router.post("/")
async def create_video(video: VideoCreate):
    try:
        created = await db.video_kegiatan.create(data=video.dict())
        return {"message": "Video created successfully", "data": created}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/")
async def get_all_video():
    return await db.video_kegiatan.find_many(include={"jurusan": True, "admin": True})


@router.get("/{id}")
async def get_video(id: int):
    video = await db.video_kegiatan.find_unique(where={"id": id}, include={"jurusan": True, "admin": True})
    if not video:
        raise HTTPException(404, "Video not found")
    return video


@router.put("/{id}")
async def update_video(id: int, data: VideoCreate):
    existing = await db.video_kegiatan.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "Video not found")
    updated = await db.video_kegiatan.update(where={"id": id}, data=data.dict())
    return {"message": "Video updated", "data": updated}


@router.delete("/{id}")
async def delete_video(id: int):
    existing = await db.video_kegiatan.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "Video not found")
    await db.video_kegiatan.delete(where={"id": id})
    return {"message": "Video deleted successfully"}
