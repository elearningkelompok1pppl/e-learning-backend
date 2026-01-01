from fastapi import APIRouter, Depends, HTTPException
from main import db
from core.permissions import authorize_access

router = APIRouter(
    prefix="/murid",
    tags=["Beranda Murid"],
    dependencies=[Depends(authorize_access)]
)

@router.get("/beranda")
async def beranda_murid(user=Depends(authorize_access)):
    # 🔒 hanya murid
    if user["role"] != "Murid":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    murid = await db.murid.find_unique(
        where={"email": user["sub"]}
    )

    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")

    # Ambil mapel sesuai jurusan
    mapel_list = await db.mata_pelajaran.find_many(
        where={
            "OR": [
                {"jurusan_id": murid.jurusan_id},
                {"jurusan_id": None}
            ]
        },
        include={"guru": True}
    )

    # Response siap FE
    result = []
    for mapel in mapel_list:
        result.append({
            "id": mapel.id,
            "nama_mapel": mapel.nama_mapel,
            "guru": mapel.guru.nama if mapel.guru else "-",
            "ringkasan": "Minggu 1 - Algoritma",
            "gambar": f"https://source.unsplash.com/400x250/?math,education&sig={mapel.id}"
        })

    return {
        "total": len(result),
        "data": result
    }
