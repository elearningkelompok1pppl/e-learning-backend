from fastapi import APIRouter, Depends, HTTPException
from core.permissions import authorize_access
from main import db

router = APIRouter(
    tags=["Murid - Materi"],
    dependencies=[Depends(authorize_access)]
)

@router.get("/{mata_pelajaran_id}")
async def get_materi_murid(
    mata_pelajaran_id: int,
    user=Depends(authorize_access)
):
    if user["role"] != "Murid":
        raise HTTPException(403, "Akses ditolak")

    murid = await db.murid.find_unique(
        where={"email": user["sub"]}
    )
    if not murid or not murid.kelas_id:
        return {"total": 0, "data": []}

    materi = await db.materi.find_many(
        where={
            "mata_pelajaran_id": mata_pelajaran_id,
            "kelas_id": murid.kelas_id
        },
        include={"guru": True},
        order={"created_at": "desc"}
    )

    return {
        "total": len(materi),
        "data": materi
    }
