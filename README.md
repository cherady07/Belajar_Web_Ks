# 🍡 Sweet Chil

Website untuk bisnis keluarga yang menjual jajan, manisan, kue custom (ulang tahun/wisuda/lamaran), dan corndog. Dibangun sebagai proyek belajar web development sekaligus alat bantu operasional nyata untuk bisnis.

## ✨ Fitur

**Untuk Customer:**

- Landing page dengan menu yang bisa dilihat langsung (data dari database, bukan hardcode)
- Form pemesanan kue custom lengkap dengan upload foto referensi
- Notifikasi diskon otomatis (badge, harga coret, countdown real-time) untuk menu yang sedang promo
- Integrasi langsung ke WhatsApp untuk konsultasi & konfirmasi pesanan

**Untuk Admin (Dashboard):**

- Login admin dengan password ter-enkripsi (hashing)
- CRUD menu (tambah/edit/hapus, termasuk upload foto)
- Kelola pesanan kue custom (ubah status, isi harga setelah nego)
- CRUD daftar harga untuk brownies & tart berdasarkan ukuran
- Kalkulasi HPP (Harga Pokok Produksi) otomatis berdasarkan resep & harga bahan baku
- CRUD bahan baku dan resep per menu
- Kelola diskon per menu dengan periode aktif otomatis

## 🛠️ Tech Stack

- **Backend:** Python (Flask)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript, Jinja2 templating
- **Keamanan:** Werkzeug (password hashing)

## 🚀 Cara Menjalankan

1. Clone repository ini

```bash
   git clone https://github.com/cherady07/Belajar_Web_Ks.git
   cd Belajar_Web_Ks
```

2. (Opsional tapi disarankan) Buat virtual environment

```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
```

3. Install dependencies

```bash
   pip install -r requirements.txt
```

4. Siapkan database (jalankan schema.sql ke database.db menggunakan SQLite)

```bash
   sqlite3 database.db
   .read schema.sql
```

5. Jalankan aplikasi

```bash
   python app.py
```

6. Buka browser ke `http://127.0.0.1:5000`

## 📁 Struktur Project

├── app.py # Entry point Flask, semua route
├── schema.sql # Struktur tabel database
├── templates/
│ ├── index.html # Landing page
│ ├── login.html # Halaman login admin
│ ├── menu/ # CRUD menu
│ ├── pesanan/ # Kelola pesanan custom
│ ├── harga/ # CRUD daftar harga
│ ├── hpp/ # HPP, bahan baku, resep
│ └── promo/ # Diskon
└── static/
├── css/ # Stylesheet per halaman
├── js/ # JavaScript (animasi, countdown, dll)
└── images/ # Foto menu & referensi customer

## 📌 Status Pengembangan

Project ini masih aktif dikembangkan. Fitur yang direncanakan selanjutnya:

- Pengumuman menu baru
- Voting ide menu dari customer
- Laporan keuntungan/revenue

---

Dibuat sebagai media belajar web development (Flask + SQLite) sambil membantu operasional bisnis keluarga.
