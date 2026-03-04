# SI-MAPAN Backend (Django REST Framework)
Repositori ini berisi logika bisnis dan API untuk Sistem Informasi Koperasi (SI-MAPAN).

## Struktur Direktori
* `/simapan_core`: Pengaturan utama Django dan routing.
* `/[nama-app]`: Modul aplikasi koperasi (auth, transaksi, dll).

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