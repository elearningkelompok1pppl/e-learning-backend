from fastapi import APIRouter, Depends, HTTPException
from main import db
from core.permissions import authorize_access

router = APIRouter(
    tags=["Guru"],
    dependencies=[Depends(authorize_access)]
)

@router.get("/murid/pending")
async def get_pending_murid(user=Depends(authorize_access)):
    if user["role"] != "Guru":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    murid_list = await db.murid.find_many(
        where={"is_verified": False}
    )

    return {
        "total": len(murid_list),
        "data": [
            {
                "id": m.id,
                "nama": m.nama,
                "email": m.email,
                "nis": m.nis,
                "nisn": m.nisn,
                "kelas_id": m.kelas_id,
                "jurusan_id": m.jurusan_id,
                "created_at": m.created_at,
            }
            for m in murid_list
        ]
    }

@router.put("/murid/{murid_id}/verify")
async def verify_murid(murid_id: int, user=Depends(authorize_access)):
    if user["role"] != "Guru":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    murid = await db.murid.find_unique(where={"id": murid_id})
    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")

    if murid.is_verified:
        raise HTTPException(status_code=400, detail="Murid sudah diverifikasi")

    # ambil guru yang login
    guru = await db.guru.find_unique(where={"email": user["sub"]})
    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    await db.murid.update(
        where={"id": murid_id},
        data={
            "is_verified": True,
            "verified_by": guru.id
        }
    )

    return {
        "message": "✅ Murid berhasil diverifikasi",
        "murid_id": murid_id,
        "verified_by": guru.nama
    }
