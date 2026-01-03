from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date, datetime
from core.permissions import authorize_access
from main import db

router = APIRouter(
    tags=["Guru - Absensi"],
    dependencies=[Depends(authorize_access)]
)

VALID_STATUS = ["Hadir", "Izin", "Sakit", "Alpha"]

# ===============================
# SCHEMA
# ===============================
class OpenAbsensi(BaseModel):
    mata_pelajaran_id: int
    kelas_id: int
    tanggal: date

class UpdateAbsensi(BaseModel):
    murid_id: int
    mata_pelajaran_id: int
    kelas_id: int
    tanggal: str
    status: str
    keterangan: str | None = None

# ===============================
# OPEN ABSENSI (VALIDASI SAJA)
# ===============================
@router.post("/open")
async def open_absensi(
    data: OpenAbsensi,
    user=Depends(authorize_access)
):
    if user["role"] != "Guru":
        raise HTTPException(403, "Akses ditolak")

    # cuma validasi konteks (tidak insert DB)
    return {
        "message": "Absensi dibuka",
        "tanggal": data.tanggal,
        "kelas_id": data.kelas_id,
        "mata_pelajaran_id": data.mata_pelajaran_id
    }


# ===============================
# REKAP ABSENSI (SEMUA MURID WAJIB TAMPIL)
# ===============================
@router.get("/rekap")
async def rekap_absensi(
    mata_pelajaran_id: int,
    kelas_id: int,
    tanggal: str,  # ⬅️ STRING
    user=Depends(authorize_access)
):
    if user["role"] != "Guru":
        raise HTTPException(403, "Akses ditolak")

    tanggal_dt = datetime.strptime(tanggal, "%Y-%m-%d")

    murid_list = await db.murid.find_many(
        where={"kelas_id": kelas_id},
        order={"nama": "asc"}
    )

    absensi_list = await db.absensi.find_many(
        where={
            "mata_pelajaran_id": mata_pelajaran_id,
            "kelas_id": kelas_id,
            "tanggal": tanggal_dt
        }
    )

    absensi_map = {a.murid_id: a for a in absensi_list}

    hasil = []
    for murid in murid_list:
        data = absensi_map.get(murid.id)
        hasil.append({
            "murid_id": murid.id,
            "nama": murid.nama,
            "status": data.status if data else "Alpha",
            "keterangan": data.keterangan if data else None
        })

    return {
        "tanggal": tanggal,
        "total_murid": len(hasil),
        "data": hasil
    }

# ===============================
# UPDATE / INSERT ABSENSI
# ===============================
@router.put("/update")
async def update_absensi(
    data: UpdateAbsensi,
    user=Depends(authorize_access)
):
    if user["role"] != "Guru":
        raise HTTPException(403, "Akses ditolak")

    if data.status not in VALID_STATUS:
        raise HTTPException(400, "Status tidak valid")

    try:
        tanggal_dt = datetime.strptime(data.tanggal, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Format tanggal harus YYYY-MM-DD")

    guru = await db.guru.find_unique(where={"email": user["sub"]})
    if not guru:
        raise HTTPException(404, "Guru tidak ditemukan")

    existing = await db.absensi.find_first(
        where={
            "murid_id": data.murid_id,
            "mata_pelajaran_id": data.mata_pelajaran_id,
            "kelas_id": data.kelas_id,
            "tanggal": tanggal_dt
        }
    )

    if existing:
        await db.absensi.update(
            where={"id": existing.id},
            data={
                "status": data.status,
                "keterangan": data.keterangan
            }
        )
    else:
        await db.absensi.create(
            data={
                "murid_id": data.murid_id,
                "mata_pelajaran_id": data.mata_pelajaran_id,
                "kelas_id": data.kelas_id,
                "tanggal": tanggal_dt,
                "status": data.status,
                "keterangan": data.keterangan,
                "guru_id": guru.id   # ⬅️ BENER (bukan user["id"])
            }
        )

    return {"message": "Absensi berhasil diperbarui"}
