# Laporan Pengerjaan Individu - Nafia Levana Aulia

## Informasi Pekerja
- **Nama:** Nafia Levana Aulia
- **Role / Branch:** `feat/nafia`

## Daftar Product Backlog Item (PBI) yang Dikerjakan
Saya bertanggung jawab atas pengembangan fitur-fitur fundamental yang berkaitan dengan autentikasi keamanan, registrasi awal, dan siklus inti peminjaman anggota.

### 1. PBI-1: Auth: Login (Priority: Must Have)
- **Deskripsi:** Mengembangkan fungsionalitas login yang aman menggunakan hashing password dan implementasi token JWT berbasis role.
- **Tujuan:** Memastikan hanya pengguna dengan kredensial valid yang dapat mengakses dashboard sesuai perannya.

### 2. PBI-2: Auth: Logout (Priority: Must Have)
- **Deskripsi:** Mengembangkan mekanisme terminasi sesi pengguna (logout) dengan menghapus token dari penyimpanan lokal klien.
- **Tujuan:** Menjaga keamanan akun setelah pengguna selesai menggunakan aplikasi.

### 3. PBI-3: Registrasi Calon Anggota Baru (Priority: Must Have)
- **Deskripsi:** Membuat form pendaftaran publik (Guest Access) yang menerima input biodata lengkap dan file identitas (KTP).
- **Tujuan:** Mendokumentasikan data pendaftar baru ke dalam sistem dengan status awal `PENDING`.

### 4. PBI-11: Tambah Form Pengajuan Pinjaman (Priority: Must Have)
- **Deskripsi:** Mengembangkan halaman form bagi anggota aktif untuk mengajukan pinjaman, lengkap dengan fitur simulasi kalkulasi cicilan otomatis berdasarkan nominal dan tenor.
- **Tujuan:** Memfasilitasi anggota dalam mengajukan kredit secara mandiri.

### 5. PBI-12: Lihat Daftar Pengajuan Pinjaman (Priority: Must Have)
- **Deskripsi:** Mengembangkan antarmuka tabel bagi Manajer untuk melihat dan memfilter seluruh draf pengajuan pinjaman yang masuk dengan status `SUBMITTED`.
- **Tujuan:** Memudahkan manajer menyeleksi antrean permohonan kredit.

### 6. PBI-20: Update Proses Settlement Anggota Resign (Priority: Should Have)
- **Deskripsi:** Mengembangkan fungsionalitas kalkulasi akhir (Total Simpanan dikurangi Sisa Hutang) saat anggota mengajukan penutupan akun.
- **Tujuan:** Memastikan perhitungan hak dan kewajiban akhir anggota dilakukan secara otomatis dan transparan.