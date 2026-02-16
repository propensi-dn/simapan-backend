# SI-MAPAN Backend (Django REST Framework)
Repositori ini berisi logika bisnis dan API untuk Sistem Informasi Koperasi (SI-MAPAN).

## Struktur Direktori
* `/simapan_core`: Pengaturan utama Django dan routing.
* `/[nama-app]`: Modul aplikasi koperasi (auth, transaksi, dll).

## Panduan Instalasi Lokal (Reproducibility)
1. Buat environment: `python -m venv venv`
2. Aktivasi: `venv\Scripts\activate` (Windows) atau `source venv/bin/activate` (Mac/Linux)
3. Install dependensi: `pip install -r requirements.txt`
4. Jalankan server: `python manage.py runserver`

# Laporan Pengerjaan Individu - Naila

## Informasi Pekerja
- **Nama:** Naila
- **Role / Branch:** `feat/Naila`

## Daftar Product Backlog Item (PBI) yang Dikerjakan
Saya berfokus pada modul pelaporan komprehensif (MIS/EIS) dan pengembangan dasbor analitik, baik untuk pengguna tingkat Manajer maupun Anggota.

### 1. PBI-16: Lihat Tagihan Bulanan (Priority: Must Have)
- **Deskripsi:** Mengembangkan tabel daftar seluruh angsuran aktif berdasarkan filter bulan berjalan.
- **Tujuan:** Memudahkan petugas memonitor arus kas masuk dari sektor kredit.

### 2. PBI-21: Lihat Laporan Kas Periodik (Priority: Must Have)
- **Deskripsi:** Membuat laporan rekapitulasi yang menggabungkan seluruh transaksi debet (masuk) dan kredit (keluar) berdasarkan filter rentang tanggal.
- **Tujuan:** Alat bantu manajer untuk memvalidasi fisik uang tunai harian di laci kasir (rekonsiliasi kas).

### 3. PBI-22: Lihat List Kredit Macet (Priority: Must Have)
- **Deskripsi:** Mengembangkan fitur filter otomatis (*Overdue Finder*) yang menampilkan daftar anggota dengan tagihan melewati *due date* beserta jumlah hari keterlambatannya.
- **Tujuan:** Memberikan peringatan dini kepada pengurus untuk segera melakukan penagihan utang.

### 4. PBI-24: Lihat Dashboard Keuangan Pribadi (Priority: Must Have)
- **Deskripsi:** Mengembangkan halaman dasbor utama bagi Anggota (setelah login) yang menampilkan Total Simpanan, Sisa Hutang, dan 10 riwayat transaksi terakhir.
- **Tujuan:** Memberikan transparansi penuh dan kemudahan akses informasi personal bagi anggota.

### 5. PBI-26: Lihat Statistik Pertumbuhan Anggota (Priority: Should Have)
- **Deskripsi:** Mengembangkan grafik (*Bar/Line Chart*) yang memetakan tren pendaftaran anggota baru secara *time-series* (per bulan/tahun).
- **Tujuan:** Menyediakan visualisasi data bagi manajemen untuk mengevaluasi kinerja pertumbuhan organisasi.