# Laporan Pengerjaan Individu - Anggun

## Informasi Pekerja
- **Nama:** Anggun
- **Role / Branch:** `feat/anggun`

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
- **Tujuan:** Memfasilitasi anggota mengakses dana tabungan mereka secara aman.

### 6. PBI-19: Update Status Pengajuan Penarikan Dana (Priority: Should Have)
- **Deskripsi:** Mengembangkan logika petugas untuk memproses transfer penarikan dan memotong saldo anggota yang berstatus `PENDING` menjadi `COMPLETED`.
- **Tujuan:** Memastikan pencatatan kas keluar akurat dan saldo anggota terpotong dengan benar.