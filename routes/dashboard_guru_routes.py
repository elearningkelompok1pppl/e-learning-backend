from fastapi import APIRouter, Depends, HTTPException
from main import db
from core.security import get_current_user
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
    guru = await db.guru.find_unique(where={"email": guru_email})

    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    guru_id = guru.id   # sekarang aman

    jumlah_murid = await db.murid.count(
        where={"kelas": {"wali_kelas_id": guru_id}}
    )

    jumlah_materi = await db.materi.count(
        where={"guru_id": guru_id}
    )

    jumlah_tugas = await db.tugas.count(
        where={"guru_id": guru_id}
    )

    murid_pending = await db.murid.count(
        where={"is_verified": False}
    )

    rapor_records = await db.rapor.find_many(
        where={"guru_id": guru_id}
    )

    nilai_akhir_list = [r.nilai_akhir for r in rapor_records if r.nilai_akhir is not None]

    rata_rata_nilai = (
        sum(nilai_akhir_list)/len(nilai_akhir_list) if nilai_akhir_list else None
    )

    hadir = await db.absensi.count(
        where={"guru_id": guru_id, "status": "Hadir"}
    )

    total_absensi = await db.absensi.count(
        where={"guru_id": guru_id}
    )

    persentase_kehadiran = (
        (hadir / total_absensi) * 100 if total_absensi > 0 else None
    )

    return {
        "guru": guru.nama,
        "jumlah_murid": jumlah_murid,
        "jumlah_materi": jumlah_materi,
        "jumlah_tugas": jumlah_tugas,
        "murid_pending": murid_pending,
        "rata_nilai": rata_rata_nilai,
        "kehadiran": persentase_kehadiran
    }
