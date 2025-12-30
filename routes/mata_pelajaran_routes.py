from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional
from core.permissions import authorize_access
from main import db

router = APIRouter(
    tags=["Guru - Mata Pelajaran"],
    dependencies=[Depends(authorize_access)]
)

# ===============================
# CREATE MATA PELAJARAN (GURU)
# ===============================
@router.post("")
async def create_mata_pelajaran(
    kode_mapel: Optional[str] = Body(None),
    nama_mapel: str = Body(...),
    deskripsi: Optional[str] = Body(None),
    kategori: Optional[str] = Body("Umum"),
    tingkat_kesulitan: Optional[str] = Body("Pemula"),
    jurusan_id: Optional[int] = Body(None),
    kelas_id: int = Body(...),  # ✅ NUMERIK
    user=Depends(authorize_access)
):
    if user["role"] != "Guru":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    guru = await db.guru.find_unique(where={"email": user["sub"]})
    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    # ✅ validasi kelas
    kelas = await db.kelas.find_unique(where={"id": kelas_id})
    if not kelas:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")

    # ✅ validasi jurusan (opsional)
    if jurusan_id:
        jurusan = await db.jurusan.find_unique(where={"id": jurusan_id})
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
            "kelas_id": kelas_id,
            "guru_id": guru.id,
        }
    )

    return {
        "message": "Mata pelajaran berhasil ditambahkan",
        "data": mapel
    }

# ===============================
# GET MATA PELAJARAN MURID
# ===============================
@router.get("/murid", status_code=200)
async def get_mata_pelajaran_murid(user=Depends(authorize_access)):
    if user["role"] != "Murid":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    murid = await db.murid.find_unique(
        where={"email": user["sub"]}
    )
    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")

    if not murid.kelas_id:
        return {"total": 0, "data": []}

    mapel_list = await db.mata_pelajaran.find_many(
        where={"kelas_id": murid.kelas_id},
        include={
            "kelas": True,
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
async def get_mata_pelajaran_guru(user=Depends(authorize_access)):
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
            "kelas": True,
            "jurusan": True,
            "guru": True
        },
        order={"created_at": "desc"}
    )

    return {
        "total": len(mapel_list),
        "data": mapel_list
    }
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional
from core.permissions import authorize_access
from main import db

router = APIRouter(
    tags=["Guru - Mata Pelajaran"],
    dependencies=[Depends(authorize_access)]
)

# ===============================
# CREATE MATA PELAJARAN (GURU)
# ===============================
@router.post("")
async def create_mata_pelajaran(
    kode_mapel: Optional[str] = Body(None),
    nama_mapel: str = Body(...),
    deskripsi: Optional[str] = Body(None),
    kategori: Optional[str] = Body("Umum"),
    tingkat_kesulitan: Optional[str] = Body("Pemula"),
    jurusan_id: Optional[int] = Body(None),
    kelas_id: int = Body(...),  # ✅ NUMERIK
    user=Depends(authorize_access)
):
    if user["role"] != "Guru":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    guru = await db.guru.find_unique(where={"email": user["sub"]})
    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    # ✅ validasi kelas
    kelas = await db.kelas.find_unique(where={"id": kelas_id})
    if not kelas:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")

    # ✅ validasi jurusan (opsional)
    if jurusan_id:
        jurusan = await db.jurusan.find_unique(where={"id": jurusan_id})
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
            "kelas_id": kelas_id,
            "guru_id": guru.id,
        }
    )

    return {
        "message": "Mata pelajaran berhasil ditambahkan",
        "data": mapel
    }

# ===============================
# GET MATA PELAJARAN MURID
# ===============================
@router.get("/murid", status_code=200)
async def get_mata_pelajaran_murid(user=Depends(authorize_access)):
    if user["role"] != "Murid":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    murid = await db.murid.find_unique(
        where={"email": user["sub"]}
    )
    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")

    if not murid.kelas_id:
        return {"total": 0, "data": []}

    mapel_list = await db.mata_pelajaran.find_many(
        where={"kelas_id": murid.kelas_id},
        include={
            "kelas": True,
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
async def get_mata_pelajaran_guru(user=Depends(authorize_access)):
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
            "kelas": True,
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
# DELETE MATA PELAJARAN (GURU)
# ===============================
@router.delete("/{mapel_id}", status_code=200)
async def delete_mata_pelajaran(
    mapel_id: int,
    user=Depends(authorize_access)
):
    if user["role"] != "Guru":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    guru = await db.guru.find_unique(
        where={"email": user["sub"]}
    )
    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    mapel = await db.mata_pelajaran.find_unique(
        where={"id": mapel_id}
    )
    if not mapel:
        raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")

    # 🔐 pastikan mapel milik guru tsb
    if mapel.guru_id != guru.id:
        raise HTTPException(
            status_code=403,
            detail="Anda tidak berhak menghapus mata pelajaran ini"
        )

    await db.mata_pelajaran.delete(
        where={"id": mapel_id}
    )

    return {
        "message": "Mata pelajaran berhasil dihapus 🗑️",
        "id": mapel_id
    }

