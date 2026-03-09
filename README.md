# Laporan Pengerjaan Individu - Anggun

## Informasi Pekerja
- **Nama:** Anggun
- **Role / Branch:** `feat/anggun`

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

## Daftar Product Backlog Item (PBI) yang Dikerjakan
Saya bertanggung jawab atas antarmuka dan logika yang berkaitan dengan proses verifikasi keanggotaan, penarikan dana, dan analisis kelayakan kredit oleh Manajer.

### 1. PBI-4: Lihat Daftar Calon Anggota Baru (Priority: Must Have)
- **Deskripsi:** Menyediakan tabel data berisi daftar pendaftar yang masih berstatus `PENDING`.
- **Tujuan:** Memudahkan petugas memonitor antrean calon anggota baru.

### 2. PBI-5: Update Status Calon Anggota Baru (Priority: Must Have)
- **Deskripsi:** Mengembangkan tombol aksi dan logika untuk menyetujui (Approve) atau menolak (Reject) pendaftar, mengubah status dari `PENDING` menjadi `VERIFIED`.
- **Tujuan:** Memastikan keabsahan data anggota sebelum diaktifkan.

### 3. PBI-13: Lihat Profil Kelayakan Anggota untuk Approval Pinjaman (Priority: Must Have)
- **Deskripsi:** Mengembangkan *scorecard* ringkasan finansial (Total Simpanan vs Total Hutang & Riwayat Macet) milik pemohon pinjaman.
- **Tujuan:** Memberikan gambaran data yang objektif kepada Manajer sebelum menyetujui kredit.

### 4. PBI-14: Update Status Pengajuan Pinjaman (Priority: Must Have)
- **Deskripsi:** Mengembangkan fitur persetujuan pinjaman yang akan mengubah status dari `SUBMITTED` menjadi `APPROVED` atau `REJECTED` (dengan alasan).
- **Tujuan:** Mendokumentasikan keputusan kredit secara sistematis.

### 5. PBI-18: Tambah Form Pengajuan Penarikan Dana (Priority: Should Have)
- **Deskripsi:** Membuat form bagi anggota untuk menarik simpanan sukarela dengan validasi limit saldo secara real-time.


# Laporan Pengerjaan Individu - Karina

## Informasi Pekerja
- **Nama:** Karina
- **Role / Branch:** `feat/karina`

## Daftar Product Backlog Item (PBI) yang Dikerjakan
Saya bertanggung jawab penuh atas modul mutasi simpanan rutin (masuk), pengelolaan pembayaran angsuran kredit, serta kalkulasi estimasi keuntungan koperasi (SHU).

### 1. PBI-8: Tambah Setoran Rutin (Priority: Must Have)
- **Deskripsi:** Mengembangkan form bagi anggota untuk menyetorkan Simpanan Wajib atau Sukarela beserta upload bukti transfernya.
- **Tujuan:** Memfasilitasi anggota untuk menabung secara digital dan mandiri.

### 2. PBI-9: Lihat Riwayat Setoran Rutin (Priority: Must Have)
- **Deskripsi:** Membuat antarmuka tabel bagi anggota untuk melihat status transaksi setoran mereka (Pending/Success).
- **Tujuan:** Memberikan transparansi mutasi masuk kepada anggota.

### 3. PBI-10: Update Saldo Setoran Rutin Anggota (Priority: Must Have)
- **Deskripsi:** Mengembangkan logika validasi petugas untuk mengonfirmasi setoran yang masuk, yang akan secara otomatis menambah saldo anggota.
- **Tujuan:** Memastikan pembukuan kas masuk sinkron dengan saldo dompet pengguna.

### 4. PBI-17: Update Pembayaran Tagihan Bulanan (Priority: Must Have)
- **Deskripsi:** Mengembangkan fitur pembayaran cicilan yang memiliki logika matematis untuk memecah secara otomatis proporsi pelunasan Pokok dan pendapatan Jasa (Bunga).
- **Tujuan:** Memastikan perhitungan sisa hutang dan pencatatan laba bunga berjalan dengan sangat presisi.

### 5. PBI-23: Lihat Estimasi SHU (Priority: Should Have)
- **Deskripsi:** Membuat kalkulator dasbor yang mengagregasi seluruh pendapatan jasa pinjaman dikurangi biaya operasional untuk menghasilkan angka Sisa Hasil Usaha (SHU) sementara.
- **Tujuan:** Menampilkan gambaran profitabilitas koperasi secara *real-time*.
- **Tujuan:** Memfasilitasi anggota mengakses dana tabungan mereka secara aman.

### 6. PBI-19: Update Status Pengajuan Penarikan Dana (Priority: Should Have)
- **Deskripsi:** Mengembangkan logika petugas untuk memproses transfer penarikan dan memotong saldo anggota yang berstatus `PENDING` menjadi `COMPLETED`.
- **Tujuan:** Memastikan pencatatan kas keluar akurat dan saldo anggota terpotong dengan benar.
