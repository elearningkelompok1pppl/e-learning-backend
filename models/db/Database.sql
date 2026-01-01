-- Tabel Admin
CREATE TABLE IF NOT EXISTS admin (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'Admin' CHECK (role IN ('Super Admin', 'Admin')),
    foto_profil VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Jurusan
CREATE TABLE IF NOT EXISTS jurusan (
    id SERIAL PRIMARY KEY,
    kode_jurusan VARCHAR(20) UNIQUE NOT NULL,
    nama_jurusan VARCHAR(100) NOT NULL,
    deskripsi TEXT,
    visi TEXT,
    misi TEXT,
    prospek_kerja TEXT,
    foto_jurusan VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Aktif' CHECK (status IN ('Aktif', 'Nonaktif')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Guru
CREATE TABLE IF NOT EXISTS guru (
    id SERIAL PRIMARY KEY,
    nip VARCHAR(50) UNIQUE,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    mata_pelajaran VARCHAR(100),
    foto_profil VARCHAR(255),
    no_telepon VARCHAR(20),
    alamat TEXT,
    status VARCHAR(20) DEFAULT 'Aktif' CHECK (status IN ('Aktif', 'Nonaktif')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Kelas
CREATE TABLE IF NOT EXISTS kelas (
    id SERIAL PRIMARY KEY,
    nama_kelas VARCHAR(50) NOT NULL,
    tingkat VARCHAR(5) NOT NULL CHECK (tingkat IN ('X', 'XI', 'XII')),
    jurusan_id INTEGER NOT NULL REFERENCES jurusan(id),
    tahun_ajaran VARCHAR(20) NOT NULL,
    wali_kelas_id INTEGER REFERENCES guru(id),
    kapasitas INTEGER DEFAULT 36,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (nama_kelas, tingkat, jurusan_id, tahun_ajaran)
);

-- ------------------------------ 
-- Tabel Murid
CREATE TABLE IF NOT EXISTS murid (
    id SERIAL PRIMARY KEY,
    nis VARCHAR(50) UNIQUE,
    nisn VARCHAR(50) UNIQUE,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    kelas_id INTEGER REFERENCES kelas(id),
    jurusan_id INTEGER REFERENCES jurusan(id),
    foto_profil VARCHAR(255),
    tanggal_lahir DATE,
    jenis_kelamin VARCHAR(1) CHECK (jenis_kelamin IN ('L', 'P')),
    no_telepon VARCHAR(20),
    alamat TEXT,
    nama_ortu VARCHAR(100),
    no_telepon_ortu VARCHAR(20),
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by INTEGER REFERENCES guru(id),
    status VARCHAR(20) DEFAULT 'Aktif' CHECK (status IN ('Aktif', 'Alumni', 'Keluar')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Partner/Perusahaan
CREATE TABLE IF NOT EXISTS partner (
    id SERIAL PRIMARY KEY,
    nama_perusahaan VARCHAR(150) NOT NULL,
    bidang_usaha VARCHAR(100),
    alamat TEXT,
    no_telepon VARCHAR(20),
    email VARCHAR(100),
    website VARCHAR(255),
    logo_perusahaan VARCHAR(255),
    pic_nama VARCHAR(100),
    pic_jabatan VARCHAR(100),
    pic_telepon VARCHAR(20),
    deskripsi TEXT,
    status_kerjasama VARCHAR(20) DEFAULT 'Aktif' CHECK (status_kerjasama IN ('Aktif', 'Nonaktif')),
    tanggal_mulai_kerjasama DATE,
    tanggal_akhir_kerjasama DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Relasi Partner dengan Jurusan
CREATE TABLE IF NOT EXISTS partner_jurusan (
    id SERIAL PRIMARY KEY,
    partner_id INTEGER REFERENCES partner(id) ON DELETE CASCADE,
    jurusan_id INTEGER REFERENCES jurusan(id) ON DELETE CASCADE,
    jenis_kerjasama VARCHAR(50) CHECK (jenis_kerjasama IN ('PKL', 'Rekrutmen', 'Magang', 'Workshop', 'Lainnya')),
    deskripsi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Berita
CREATE TABLE IF NOT EXISTS berita (
    id SERIAL PRIMARY KEY,
    judul VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    konten TEXT NOT NULL,
    kategori VARCHAR(50) DEFAULT 'Pengumuman' CHECK (kategori IN ('Akademik', 'Prestasi', 'Kegiatan', 'Pengumuman', 'Lainnya')),
    gambar_utama VARCHAR(255),
    penulis_id INTEGER REFERENCES admin(id),
    penulis_tipe VARCHAR(20) DEFAULT 'Admin' CHECK (penulis_tipe IN ('Admin', 'Guru')),
    status VARCHAR(20) DEFAULT 'Draft' CHECK (status IN ('Draft', 'Published')),
    views INTEGER DEFAULT 0,
    tanggal_publish TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger untuk auto update updated_at pada tabel berita
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_berita_updated_at
    BEFORE UPDATE ON berita
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------ 
-- Tabel Video Kegiatan
CREATE TABLE IF NOT EXISTS video_kegiatan (
    id SERIAL PRIMARY KEY,
    judul VARCHAR(200) NOT NULL,
    deskripsi TEXT,
    youtube_url VARCHAR(255) NOT NULL,
    youtube_id VARCHAR(50),
    kategori VARCHAR(50) DEFAULT 'Kegiatan' CHECK (kategori IN ('Ekstrakurikuler', 'Pembelajaran', 'Event', 'Prestasi', 'PKL', 'Lainnya')),
    jurusan_id INTEGER REFERENCES jurusan(id),
    thumbnail VARCHAR(255),
    views INTEGER DEFAULT 0,
    uploaded_by INTEGER REFERENCES admin(id),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Mata Pelajaran
CREATE TABLE IF NOT EXISTS mata_pelajaran (
    id SERIAL PRIMARY KEY,
    kode_mapel VARCHAR(20) UNIQUE,
    nama_mapel VARCHAR(100) NOT NULL,
    deskripsi TEXT,
    kategori VARCHAR(50) DEFAULT 'Umum' CHECK (kategori IN ('Umum', 'Produktif', 'Muatan Lokal')),
    tingkat_kesulitan VARCHAR(20) DEFAULT 'Pemula' CHECK (tingkat_kesulitan IN ('Pemula', 'Menengah', 'Lanjut')),
    jurusan_id INTEGER REFERENCES jurusan(id),
    guru_id INTEGER REFERENCES guru(id),
    kelas_id INTEGER REFERENCES kelas(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Materi
CREATE TABLE IF NOT EXISTS materi (
    id SERIAL PRIMARY KEY,
    judul VARCHAR(200) NOT NULL,
    konten TEXT NOT NULL,
    file_materi VARCHAR(255),
    tipe_file VARCHAR(20) CHECK (tipe_file IN ('PDF', 'PPT', 'DOC', 'Video', 'Lainnya')),
    mata_pelajaran_id INTEGER REFERENCES mata_pelajaran(id),
    guru_id INTEGER REFERENCES guru(id),
    kelas_id INTEGER REFERENCES kelas(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Quiz
CREATE TABLE IF NOT EXISTS quiz (
    id SERIAL PRIMARY KEY,
    judul VARCHAR(200) NOT NULL,
    deskripsi TEXT,
    mata_pelajaran_id INTEGER REFERENCES mata_pelajaran(id),
    kelas_id INTEGER REFERENCES kelas(id),
    guru_id INTEGER REFERENCES guru(id),
    durasi INTEGER, -- Durasi dalam menit
    tanggal_mulai TIMESTAMP,
    tanggal_selesai TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Draft' CHECK (status IN ('Draft', 'Active', 'Closed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Soal Quiz
CREATE TABLE IF NOT EXISTS soal_quiz (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quiz(id) ON DELETE CASCADE,
    pertanyaan TEXT NOT NULL,
    pilihan_a VARCHAR(255) NOT NULL,
    pilihan_b VARCHAR(255) NOT NULL,
    pilihan_c VARCHAR(255) NOT NULL,
    pilihan_d VARCHAR(255) NOT NULL,
    jawaban_benar VARCHAR(1) NOT NULL CHECK (jawaban_benar IN ('A', 'B', 'C', 'D')),
    bobot INTEGER DEFAULT 1
);

-- ------------------------------ 
-- Tabel Hasil Quiz
CREATE TABLE IF NOT EXISTS hasil_quiz (
    id SERIAL PRIMARY KEY,
    murid_id INTEGER REFERENCES murid(id),
    quiz_id INTEGER REFERENCES quiz(id),
    mata_pelajaran_id INTEGER REFERENCES mata_pelajaran(id),
    score DECIMAL(5,2),
    total_soal INTEGER,
    jawaban_benar INTEGER,
    waktu_mulai TIMESTAMP,
    waktu_selesai TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Preferensi Murid
CREATE TABLE IF NOT EXISTS preferensi_murid (
    id SERIAL PRIMARY KEY,
    murid_id INTEGER REFERENCES murid(id),
    mata_pelajaran_favorit VARCHAR(100),
    gaya_belajar VARCHAR(20) DEFAULT 'Visual' CHECK (gaya_belajar IN ('Visual', 'Audio', 'Kinestetik', 'Campuran')),
    minat_bidang VARCHAR(100),
    target_karir TEXT,
    hobi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_preferensi_murid_updated_at
    BEFORE UPDATE ON preferensi_murid
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------ 
-- Tabel Program PKL (Praktek Kerja Lapangan)
CREATE TABLE IF NOT EXISTS pkl (
    id SERIAL PRIMARY KEY,
    murid_id INTEGER REFERENCES murid(id),
    partner_id INTEGER REFERENCES partner(id),
    jurusan_id INTEGER REFERENCES jurusan(id),
    tanggal_mulai DATE,
    tanggal_selesai DATE,
    pembimbing_sekolah_id INTEGER REFERENCES guru(id),
    pembimbing_industri VARCHAR(100),
    nilai DECIMAL(5,2),
    keterangan TEXT,
    status VARCHAR(50) DEFAULT 'Sedang Berjalan' CHECK (status IN ('Sedang Berjalan', 'Selesai', 'Dibatalkan')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Absensi Murid
CREATE TABLE IF NOT EXISTS absensi (
    id SERIAL PRIMARY KEY,
    murid_id INTEGER REFERENCES murid(id),
    kelas_id INTEGER REFERENCES kelas(id),
    mata_pelajaran_id INTEGER REFERENCES mata_pelajaran(id),
    tanggal DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Hadir', 'Izin', 'Sakit', 'Alpha')),
    keterangan TEXT,
    guru_id INTEGER REFERENCES guru(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (murid_id, mata_pelajaran_id, tanggal)
);

-- ------------------------------ 
-- Tabel Tugas
CREATE TABLE IF NOT EXISTS tugas (
    id SERIAL PRIMARY KEY,
    judul VARCHAR(200) NOT NULL,
    deskripsi TEXT,
    mata_pelajaran_id INTEGER REFERENCES mata_pelajaran(id),
    kelas_id INTEGER REFERENCES kelas(id),
    guru_id INTEGER REFERENCES guru(id),
    deadline TIMESTAMP,
    bobot INTEGER DEFAULT 100,
    file_tugas VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Closed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Pengumpulan Tugas
CREATE TABLE IF NOT EXISTS pengumpulan_tugas (
    id SERIAL PRIMARY KEY,
    tugas_id INTEGER REFERENCES tugas(id) ON DELETE CASCADE,
    murid_id INTEGER REFERENCES murid(id),
    file_jawaban VARCHAR(255),
    keterangan TEXT,
    nilai DECIMAL(5,2),
    feedback TEXT,
    status VARCHAR(50) DEFAULT 'Belum Dinilai' CHECK (status IN ('Belum Dinilai', 'Sudah Dinilai')),
    waktu_pengumpulan TIMESTAMP,
    dinilai_oleh INTEGER REFERENCES guru(id),
    dinilai_pada TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Nilai Ujian/UTS/UAS
CREATE TABLE IF NOT EXISTS nilai_ujian (
    id SERIAL PRIMARY KEY,
    murid_id INTEGER REFERENCES murid(id),
    mata_pelajaran_id INTEGER REFERENCES mata_pelajaran(id),
    kelas_id INTEGER REFERENCES kelas(id),
    semester VARCHAR(20) NOT NULL CHECK (semester IN ('Ganjil', 'Genap')),
    tahun_ajaran VARCHAR(20) NOT NULL,
    jenis_ujian VARCHAR(50) NOT NULL CHECK (jenis_ujian IN ('UTS', 'UAS', 'Ujian Harian', 'Ujian Praktik')),
    nilai DECIMAL(5,2),
    keterangan TEXT,
    guru_id INTEGER REFERENCES guru(id),
    tanggal_ujian DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Rapor/Nilai Akhir
CREATE TABLE IF NOT EXISTS rapor (
    id SERIAL PRIMARY KEY,
    murid_id INTEGER REFERENCES murid(id),
    mata_pelajaran_id INTEGER REFERENCES mata_pelajaran(id),
    kelas_id INTEGER REFERENCES kelas(id),
    semester VARCHAR(20) NOT NULL CHECK (semester IN ('Ganjil', 'Genap')),
    tahun_ajaran VARCHAR(20) NOT NULL,
    nilai_tugas DECIMAL(5,2),
    nilai_quiz DECIMAL(5,2),
    nilai_uts DECIMAL(5,2),
    nilai_uas DECIMAL(5,2),
    nilai_praktik DECIMAL(5,2),
    nilai_akhir DECIMAL(5,2),
    predikat VARCHAR(1) CHECK (predikat IN ('A', 'B', 'C', 'D', 'E')),
    catatan TEXT,
    guru_id INTEGER REFERENCES guru(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (murid_id, mata_pelajaran_id, semester, tahun_ajaran)
);

CREATE TRIGGER update_rapor_updated_at
    BEFORE UPDATE ON rapor
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------ 
-- Tabel Aktivitas Belajar (untuk tracking engagement)
CREATE TABLE IF NOT EXISTS aktivitas_belajar (
    id SERIAL PRIMARY KEY,
    murid_id INTEGER REFERENCES murid(id),
    jenis_aktivitas VARCHAR(50) NOT NULL CHECK (jenis_aktivitas IN ('Baca Materi', 'Kerjakan Quiz', 'Upload Tugas', 'Tonton Video', 'Diskusi')),
    referensi_id INTEGER, -- ID dari materi/quiz/tugas yang terkait
    durasi INTEGER, -- Durasi dalam menit
    tanggal_aktivitas TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Laporan Performa Kelas (Summary untuk Dashboard Guru)
CREATE TABLE IF NOT EXISTS laporan_performa (
    id SERIAL PRIMARY KEY,
    kelas_id INTEGER REFERENCES kelas(id),
    mata_pelajaran_id INTEGER REFERENCES mata_pelajaran(id),
    guru_id INTEGER REFERENCES guru(id),
    periode VARCHAR(20) NOT NULL CHECK (periode IN ('Bulanan', 'Semester', 'Tahunan')),
    bulan INTEGER,
    semester VARCHAR(20) CHECK (semester IN ('Ganjil', 'Genap')),
    tahun_ajaran VARCHAR(20) NOT NULL,
    total_murid INTEGER,
    rata_rata_nilai DECIMAL(5,2),
    rata_rata_kehadiran DECIMAL(5,2),
    total_tugas_diberikan INTEGER,
    persentase_pengumpulan DECIMAL(5,2),
    total_quiz_diberikan INTEGER,
    rata_rata_quiz DECIMAL(5,2),
    murid_terbaik_id INTEGER REFERENCES murid(id),
    murid_perlu_bimbingan TEXT, -- JSON array ID murid
    catatan TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Catatan Guru tentang Murid
CREATE TABLE IF NOT EXISTS catatan_guru (
    id SERIAL PRIMARY KEY,
    murid_id INTEGER REFERENCES murid(id),
    guru_id INTEGER REFERENCES guru(id),
    mata_pelajaran_id INTEGER REFERENCES mata_pelajaran(id),
    kategori VARCHAR(50) DEFAULT 'Akademik' CHECK (kategori IN ('Prestasi', 'Perilaku', 'Akademik', 'Bimbingan', 'Lainnya')),
    catatan TEXT NOT NULL,
    is_private BOOLEAN DEFAULT FALSE, -- Hanya guru yang bisa lihat
    tanggal_catatan DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Notifikasi untuk Guru
CREATE TABLE IF NOT EXISTS notifikasi_guru (
    id SERIAL PRIMARY KEY,
    guru_id INTEGER REFERENCES guru(id),
    judul VARCHAR(200) NOT NULL,
    pesan TEXT NOT NULL,
    tipe VARCHAR(50) DEFAULT 'Sistem' CHECK (tipe IN ('Tugas Masuk', 'Quiz Selesai', 'Nilai Rendah', 'Absensi', 'Sistem', 'Lainnya')),
    is_read BOOLEAN DEFAULT FALSE,
    link VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------ 
-- Tabel Target Pembelajaran (KPI untuk Guru)
CREATE TABLE IF NOT EXISTS target_pembelajaran (
    id SERIAL PRIMARY KEY,
    guru_id INTEGER REFERENCES guru(id),
    mata_pelajaran_id INTEGER REFERENCES mata_pelajaran(id),
    kelas_id INTEGER REFERENCES kelas(id),
    semester VARCHAR(20) NOT NULL CHECK (semester IN ('Ganjil', 'Genap')),
    tahun_ajaran VARCHAR(20) NOT NULL,
    target_rata_nilai DECIMAL(5,2),
    target_kehadiran DECIMAL(5,2),
    target_ketuntasan DECIMAL(5,2), -- Persentase murid yang tuntas
    realisasi_rata_nilai DECIMAL(5,2),
    realisasi_kehadiran DECIMAL(5,2),
    realisasi_ketuntasan DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'Belum Tercapai' CHECK (status IN ('Belum Tercapai', 'Tercapai', 'Melebihi Target')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_target_pembelajaran_updated_at
    BEFORE UPDATE ON target_pembelajaran
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


--  optimasi performa pake indeks

CREATE INDEX idx_murid_kelas ON murid(kelas_id);
CREATE INDEX idx_murid_jurusan ON murid(jurusan_id);
CREATE INDEX idx_kelas_jurusan ON kelas(jurusan_id);
CREATE INDEX idx_absensi_murid_tanggal ON absensi(murid_id, tanggal);
CREATE INDEX idx_nilai_ujian_murid ON nilai_ujian(murid_id, semester, tahun_ajaran);
CREATE INDEX idx_rapor_murid ON rapor(murid_id, semester, tahun_ajaran);
CREATE INDEX idx_quiz_kelas ON quiz(kelas_id, status);
CREATE INDEX idx_tugas_kelas ON tugas(kelas_id, status);
CREATE INDEX idx_berita_status ON berita(status, tanggal_publish);