from fastapi import APIRouter, Depends, HTTPException
from core.permissions import authorize_access, check_permission
from plugin.cluster.cluster_predictor import predict_cluster_for_student
from plugin.recommendation.ai_recommendation import generate_recommendation_ai
from main import db

router = APIRouter(tags=["Cluster"],
                   dependencies=[Depends(authorize_access)])

@router.get("/status")
async def get_cluster(user=Depends(authorize_access)):

    # RBAC proteksi module cluster
    check_permission(user, "cluster")

    # role check
    if user["role"] != "Guru":
        raise HTTPException(status_code=403, detail="❌ Akses khusus Guru")

    murid = await db.murid.find_many(include={"rapor": True})

    output = []
    for m in murid:
        rapor = m.rapor[0] if m.rapor else None
        if not rapor:
            continue

        data = {
            "nilai_akhir": rapor.nilai_akhir or 0,
            "nilai_tugas": rapor.nilai_tugas or 0,
            "nilai_quiz": rapor.nilai_quiz or 0,
            "nilai_uts": rapor.nilai_uts or 0,
            "nilai_uas": rapor.nilai_uas or 0,
            "total_hadir": 110,
            "total_alpha": 3,
            "total_izin": 2,
            "tingkat_kehadiran": 93.5,
            "jumlah_tugas": 12,
            "persentase_pengumpulan": 90,
            "total_quiz": 6,
            "rata_nilai_quiz": rapor.nilai_quiz or 0,
            "total_aktivitas": 20,
            "total_durasi_belajar": 300
        }

        cluster = predict_cluster_for_student(data)

        recommendation = generate_recommendation_ai(
            student_name=m.nama,
            cluster_label=cluster,
            data=data
        )

        output.append({
            "murid_id": m.id,
            "nama": m.nama,
            "cluster": cluster,
            "recommendation": recommendation
        })

    return output