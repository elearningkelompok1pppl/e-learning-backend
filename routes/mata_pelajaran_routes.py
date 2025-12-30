from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from core.permissions import authorize_access
from main import db   # ✅ pakai instance global

router = APIRouter(
    tags=["Guru - Mata Pelajaran"],
    dependencies=[Depends(authorize_access)]
)

@router.post("")
async def create_mata_pelajaran(
    kode_mapel: Optional[str] = Body(None),
    nama_mapel: str = Body(...),
    deskripsi: Optional[str] = Body(None),
    kategori: Optional[str] = Body("Umum"),
    tingkat_kesulitan: Optional[str] = Body("Pemula"),
    jurusan_id: Optional[int] = Body(None),
    user=Depends(authorize_access)
):
    if user["role"] != "Guru":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    guru = await db.guru.find_unique(
        where={"email": user["sub"]}
    )
    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    if jurusan_id:
        jurusan = await db.jurusan.find_unique(
            where={"id": jurusan_id}
        )
        if not jurusan:
            raise HTTPException(status_code=404, detail="Jurusan tidak ditemukan")

    mapel = await db.mata_pelajaran.create(
        data={
            "kode_mapel": kode_mapel,
            "nama_mapel": nama_mapel,
            "deskripsi": deskripsi,
            "kategori": kategori,
            "tingkat_kesulitan": tingkat_kesulitan,
            "jurusan_id": jurusan_id,
            "guru_id": guru.id,
        }
    )

    return {
        "message": "Mata pelajaran berhasil ditambahkan",
        "data": mapel
    }

# ===============================
# GET MATA PELAJARAN SISWA
# ===============================
@router.get("/murid", status_code=200)
async def get_mata_pelajaran_murid(user=Depends(authorize_access)):
    if user["role"] != "Murid":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    # Ambil data murid
    murid = await db.murid.find_unique(
        where={"email": user["sub"]}
    )
    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")

    if not murid.jurusan_id:
        return {
            "total": 0,
            "data": []
        }

    # Ambil mapel sesuai jurusan murid
    mapel_list = await db.mata_pelajaran.find_many(
        where={
            "jurusan_id": murid.jurusan_id
        },
        include={
            "jurusan": True,
            "guru": True
        },
        order={"created_at": "desc"}
    )

    return {
        "total": len(mapel_list),
        "data": mapel_list
    }
# ===============================
# GET MATA PELAJARAN GURU
# ===============================
@router.get("", status_code=200)
async def get_mata_pelajaran(user=Depends(authorize_access)):
    if user["role"] != "Guru":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    guru = await db.guru.find_unique(
        where={"email": user["sub"]}
    )
    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    mapel_list = await db.mata_pelajaran.find_many(
        where={"guru_id": guru.id},
        include={
            "jurusan": True,
            "guru": True
        },
        order={"created_at": "desc"}
    )

    return {
        "total": len(mapel_list),
        "data": mapel_list
    }
