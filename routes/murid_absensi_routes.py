from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from core.permissions import authorize_access
from main import db

router = APIRouter(
    tags=["Murid - Absensi"],
    dependencies=[Depends(authorize_access)]
)

# ===============================
# AUTO HADIR SAAT MURID LOGIN
# ===============================
@router.post("/hadir")
async def murid_hadir(
    mata_pelajaran_id: int,
    tanggal: datetime,
    user=Depends(authorize_access)
):
    if user["role"] != "Murid":
        raise HTTPException(403, "Akses ditolak")

    murid = await db.murid.find_unique(where={"email": user["sub"]})
    if not murid:
        raise HTTPException(404, "Murid tidak ditemukan")

    existing = await db.absensi.find_first(
        where={
            "murid_id": murid.id,
            "mata_pelajaran_id": mata_pelajaran_id,
            "kelas_id": murid.kelas_id,
            "tanggal": tanggal
        }
    )

    if existing:
        return {"message": "Absensi sudah tercatat", "status": existing.status}

    await db.absensi.create(
        data={
            "murid_id": murid.id,
            "mata_pelajaran_id": mata_pelajaran_id,
            "kelas_id": murid.kelas_id,
            "tanggal": tanggal,
            "status": "Hadir"
        }
    )

    return {"message": "Absensi berhasil dicatat", "status": "Hadir"}


# ===============================
# CEK STATUS ABSENSI MURID
# ===============================
@router.get("/status")
async def status_absensi(
    mata_pelajaran_id: int,
    tanggal: datetime,
    user=Depends(authorize_access)
):
    murid = await db.murid.find_unique(where={"email": user["sub"]})

    absensi = await db.absensi.find_first(
        where={
            "murid_id": murid.id,
            "mata_pelajaran_id": mata_pelajaran_id,
            "kelas_id": murid.kelas_id,
            "tanggal": tanggal
        }
    )

    return {
        "status": absensi.status if absensi else "Belum Absen",
        "keterangan": absensi.keterangan if absensi else None
    }
