
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from main import db
from core.auth import hash_password, verify_password, create_access_token
from core.security import get_current_user
from datetime import date, datetime

router = APIRouter(tags=["Authentication"])

# ======================================================
# 🧩 SCHEMAS
# ======================================================
class RegisterUser(BaseModel):
    nama: str
    email: EmailStr
    password: str
    role: str 

class LoginUser(BaseModel):
    email: EmailStr
    password: str


# ======================================================
# 🧠 REGISTER USER
# ======================================================
class RegisterBase(BaseModel):
    nama: str
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class CompleteMuridProfile(BaseModel):
    nis: str
    nisn: str
    kelas_id: int
    jurusan_id: int
    tanggal_lahir: date
    jenis_kelamin: str  # 'L' / 'P'
    no_telepon: str
    alamat: str
    nama_ortu: str
    no_telepon_ortu: str


# ======================================================
# 🔧 HELPER
# ======================================================

async def email_exists(email: str) -> bool:
    try:
        admin = await db.admin.find_unique(where={"email": email})
        if admin:
            return True

        guru = await db.guru.find_unique(where={"email": email})
        if guru:
            return True

        murid = await db.murid.find_unique(where={"email": email})
        if murid:
            return True

        return False

    except Exception as e:
        print("❌ email_exists error:", e)
        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan saat pengecekan email"
        )



# ======================================================
# 🧠 REGISTER ADMIN
# ======================================================

@router.post("/register/admin")
async def register_admin(data: RegisterBase):
    if await email_exists(data.email):
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    user = await db.admin.create(
        data={
            "nama": data.nama,
            "email": data.email,
            "password": hash_password(data.password),
            "role": "Admin",
            "status": "Aktif",
        }
    )

    return {
        "message": "Admin registered successfully ✅",
        "data": {
            "id": user.id,
            "nama": user.nama,
            "email": user.email,
            "role": user.role,
        },
    }


# ======================================================
# 🧠 REGISTER GURU
# ======================================================

@router.post("/register/guru")
async def register_guru(data: RegisterBase):
    if await email_exists(data.email):
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    user = await db.guru.create(
        data={
            "nama": data.nama,
            "email": data.email,
            "password": hash_password(data.password),
            "role": "Guru",
            "status": "Aktif",
        }
    )

    return {
        "message": "Guru registered successfully ✅",
        "data": {
            "id": user.id,
            "nama": user.nama,
            "email": user.email,
            "role": user.role,
        },
    }


# ======================================================
# 🧠 REGISTER MURID (LANJUT LENGKAPI DATA)
# ======================================================

@router.post("/register/murid")
async def register_murid(data: RegisterBase):
    if await email_exists(data.email):
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    murid = await db.murid.create(
        data={
            "nama": data.nama,
            "email": data.email,
            "password": hash_password(data.password),
            "role": "Murid",
            "is_verified": False,
            "status": "Aktif",
        }
    )

    registration_token = create_access_token({
        "sub": murid.email,
        "role": "Murid-Registration",
    })


    return {
        "message": "Registrasi murid berhasil. Silakan lengkapi data 📋",
        "registration_token": registration_token,
        "next_step": "/auth/murid/complete-profile",
    }


# ======================================================
# 📝 LENGKAPI DATA MURID (PAKAI TOKEN REGISTRASI)
# ======================================================

@router.put("/murid/complete-profile")
async def complete_murid_profile(
    data: CompleteMuridProfile,
    current_user=Depends(get_current_user),
):
    if current_user["role"] != "Murid-Registration":
        raise HTTPException(status_code=403, detail="Token tidak valid")

    murid = await db.murid.find_unique(
        where={"email": current_user["sub"]}
    )

    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")

    if murid.is_verified:
        raise HTTPException(status_code=400, detail="Akun sudah diverifikasi")

    await db.murid.update(
        where={"id": murid.id},
        data={
            "nis": data.nis,
            "nisn": data.nisn,
            "kelas_id": data.kelas_id,
            "jurusan_id": data.jurusan_id,

            # ✅ FIX PALING BENAR
            "tanggal_lahir": datetime.combine(
                data.tanggal_lahir,
                datetime.min.time()
            ),

            "jenis_kelamin": data.jenis_kelamin,
            "no_telepon": data.no_telepon,
            "alamat": data.alamat,
            "nama_ortu": data.nama_ortu,
            "no_telepon_ortu": data.no_telepon_ortu,
        },
    )

    return {
        "message": "Data lengkap ✅ Menunggu verifikasi guru ⏳"
    }

# ======================================================
# 🔐 LOGIN USER
# ======================================================
@router.post("/login")
async def login_user(data: LoginUser):
    admin = await db.admin.find_unique(where={"email": data.email})
    guru = await db.guru.find_unique(where={"email": data.email})
    murid = await db.murid.find_unique(where={"email": data.email})

    if admin:
        user, role = admin, "Admin"
    elif guru:
        user, role = guru, "Guru"
    elif murid:
        user, role = murid, "Murid"
        if not user.is_verified:
            raise HTTPException(403, "Akun belum diverifikasi oleh guru")
    else:
        raise HTTPException(404, "Email tidak ditemukan")

    if not verify_password(data.password, user.password):
        raise HTTPException(401, "Password salah")

    token = create_access_token({"sub": user.email, "role": role})

    return {
        "message": "Login berhasil",
        "access_token": token,
        "token_type": "bearer",
        "role": role,
        "user": {"nama": user.nama, "email": user.email},
    }
