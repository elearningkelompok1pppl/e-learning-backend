from fastapi import APIRouter, Depends, HTTPException
from main import db
from core.auth import get_current_user
from core.permissions import authorize_access

router = APIRouter(
    tags=["Dashboard Guru"],
    dependencies=[Depends(authorize_access)]  
)

# Middleware untuk memastikan login adalah guru
async def guru_only(user=Depends(get_current_user)):
    if user["role"] != "Guru":
        raise HTTPException(status_code=403, detail="Akses khusus Guru")
    return user


@router.get("/dashboard")
async def get_dashboard_guru(user=Depends(guru_only)):

    guru_email = user["sub"]

    # cari guru berdasarkan email
    guru = await db.guru.find_unique(where={"email": guru_email})

    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    # jumlah murid di kelas bimbingan — FIX
    jumlah_murid = await db.murid.count(
        where={"kelas_id": guru.id}   # ganti sesuai model kamu
    )

    # jumlah tugas dibuat oleh guru
    jumlah_tugas = await db.tugas.count(
        where={"guru_id": guru.id}
    )

    # --- FIX PENENTUAN RATA-RATA NILAI (TANPA aggregate) ---
    nilai_records = await db.nilai_ujian.find_many(
        where={"guru_id": guru.id}
    )

    if nilai_records:
        total = sum([n.nilai for n in nilai_records if n.nilai is not None])
        jumlah = len([n.nilai for n in nilai_records if n.nilai is not None])
        rata_nilai = total / jumlah if jumlah > 0 else None
    else:
        rata_nilai = None

    # rata-rata kehadiran murid
    hadir = await db.absensi.count(
        where={"guru_id": guru.id, "status": "Hadir"}
    )

    total_absensi = await db.absensi.count(
        where={"guru_id": guru.id}
    )

    persentase_kehadiran = (
        (hadir / total_absensi) * 100 if total_absensi > 0 else None
    )

    return {
        "guru": guru.nama,
        "jumlah_murid": jumlah_murid,
        "jumlah_tugas": jumlah_tugas,
        "rata_nilai": rata_nilai,
        "kehadiran_percent": persentase_kehadiran
    }
