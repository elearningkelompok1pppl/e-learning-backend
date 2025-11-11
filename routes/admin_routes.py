from fastapi import APIRouter, HTTPException
from generated.prisma import Prisma
from pydantic import BaseModel
from main import db

router = APIRouter()

class AdminCreate(BaseModel):
    nama: str
    email: str
    password: str
    role: str = "Admin"
    foto_profil: str | None = None

@router.post("/")
async def create_admin(admin: AdminCreate):
    created = await db.admin.create(data=admin.dict())
    return {"message": "Admin created successfully", "data": created}

@router.get("/")
async def get_all_admin():
    admins = await db.admin.find_many()
    return admins

@router.get("/{id}")
async def get_admin(id: int):
    admin = await db.admin.find_unique(where={"id": id})
    if not admin:
        raise HTTPException(404, "Admin not found")
    return admin

@router.put("/{id}")
async def update_admin(id: int, data: AdminCreate):
    updated = await db.admin.update(where={"id": id}, data=data.dict())
    return {"message": "Admin updated", "data": updated}

@router.delete("/{id}")
async def delete_admin(id: int):
    await db.admin.delete(where={"id": id})
    return {"message": "Admin deleted"}
