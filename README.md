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