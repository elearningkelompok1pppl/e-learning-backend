from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from main import db
from core.auth import hash_password, verify_password, create_access_token

# ✅ HAPUS prefix di sini biar tidak dobel dengan main.py
router = APIRouter(tags=["Authentication"])

# ======================================================
# 🧩 SCHEMAS
# ======================================================
class RegisterUser(BaseModel):
    nama: str
    email: EmailStr
    password: str
    role: str  # "Admin", "Guru", atau "Murid"

class LoginUser(BaseModel):
    email: EmailStr
    password: str


# ======================================================
# 🧠 REGISTER USER
# ======================================================
@router.post("/register")
async def register_user(data: RegisterUser):
    try:
        # Cek apakah email sudah digunakan di salah satu tabel
        existing_admin = await db.admin.find_unique(where={"email": data.email})
        existing_guru = await db.guru.find_unique(where={"email": data.email})
        existing_murid = await db.murid.find_unique(where={"email": data.email})

        if existing_admin or existing_guru or existing_murid:
            raise HTTPException(status_code=400, detail="Email sudah terdaftar")

        hashed_pw = hash_password(data.password)

        # Role-based registration
        role = data.role.lower()
        if role == "admin":
            user = await db.admin.create(
                data={
                    "nama": data.nama,
                    "email": data.email,
                    "password": hashed_pw,
                    "role": "Admin",
                    "status": "Aktif",
                }
            )
        elif role == "guru":
            user = await db.guru.create(
                data={
                    "nama": data.nama,
                    "email": data.email,
                    "password": hashed_pw,
                    "status": "Aktif",
                    "role": "Guru",
                }
            )
        elif role == "murid":
            user = await db.murid.create(
                data={
                    "nama": data.nama,
                    "email": data.email,
                    "password": hashed_pw,
                    "role": "Murid",
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Role tidak dikenali")

        return {
            "message": f"{data.role} registered successfully ✅",
            "data": {"id": user.id, "nama": user.nama, "email": user.email, "role": user.role},
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan server: {str(e)}")


# ======================================================
# 🔐 LOGIN USER
# ======================================================
@router.post("/login")
async def login_user(data: LoginUser):
    try:
        # Cari user di semua tabel berdasarkan email
        user = None
        role = None

        admin = await db.admin.find_unique(where={"email": data.email})
        guru = await db.guru.find_unique(where={"email": data.email})
        murid = await db.murid.find_unique(where={"email": data.email})

        if admin:
            user = admin
            role = "Admin"
        elif guru:
            user = guru
            role = "Guru"
        elif murid:
            user = murid
            role = "Murid"
        else:
            raise HTTPException(status_code=404, detail="Email tidak ditemukan")

        # Verifikasi password
        if not verify_password(data.password, user.password):
            raise HTTPException(status_code=401, detail="Password salah")

        # Buat token JWT
        token = create_access_token({"sub": user.email, "role": role})

        return {
            "message": "Login berhasil ✅",
            "access_token": token,
            "token_type": "bearer",
            "role": role,
            "user": {"nama": user.nama, "email": user.email},
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan server: {str(e)}")
