# routes/admin_routes.py — Manajemen Data Admin (RBAC Protected)
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from core.permissions import authorize_access, check_permission
from main import db

router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(authorize_access)]  
)

# SCHEMA: Data Admin
class AdminCreate(BaseModel):
    nama: str = Field(..., description="Nama lengkap admin")
    email: EmailStr = Field(..., description="Email unik admin")
    password: str = Field(..., description="Password admin")
    role: str = Field(default="Admin", description="Role tetap Admin")
    foto_profil: str | None = Field(default=None, description="URL foto profil (opsional)")

# CREATE — Tambah Admin Baru
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_admin(admin: AdminCreate, user=Depends(authorize_access)):
    check_permission(user, "admin")
    existing = await db.admin.find_unique(where={"email": admin.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    created = await db.admin.create(data=admin.dict())
    return {"message": "✅ Admin berhasil dibuat", "data": created}

# READ — Ambil Semua Admin
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_admin(user=Depends(authorize_access)):
    check_permission(user, "admin")
    admins = await db.admin.find_many()
    return {"total": len(admins), "data": admins}

# READ — Ambil Admin Berdasarkan ID
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_admin_by_id(id: int, user=Depends(authorize_access)):
    check_permission(user, "admin")
    admin = await db.admin.find_unique(where={"id": id})
    if not admin:
        raise HTTPException(status_code=404, detail="❌ Admin tidak ditemukan")
    return {"data": admin}

# UPDATE — Ubah Data Admin Berdasarkan ID
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_admin(id: int, data: AdminCreate, user=Depends(authorize_access)):
    check_permission(user, "admin")
    existing = await db.admin.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Admin tidak ditemukan")

    updated = await db.admin.update(where={"id": id}, data=data.dict())
    return {"message": "✅ Data admin berhasil diperbarui", "data": updated}

# DELETE — Hapus Admin Berdasarkan ID
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_admin(id: int, user=Depends(authorize_access)):
    check_permission(user, "admin")
    existing = await db.admin.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Admin tidak ditemukan")

    await db.admin.delete(where={"id": id})
    return {"message": "🗑️ Admin berhasil dihapus"}
