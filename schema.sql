-- Tabel menu (produk siap jual: corndog, manisan, jajan)
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY,
    nama TEXT,
    harga INTEGER,
    stok INTEGER,
    kategori TEXT,
    foto TEXT
);

-- Tabel daftar_harga (kamus harga fix untuk brownies/tart berdasarkan ukuran)
CREATE TABLE IF NOT EXISTS daftar_harga (
    id INTEGER PRIMARY KEY,
    jenis_kue TEXT,
    ukuran TEXT,
    harga INTEGER
);

-- Tabel pesanan_custom (request kue custom dari customer)
CREATE TABLE IF NOT EXISTS pesanan_custom (
    id INTEGER PRIMARY KEY,
    nama_pemesan TEXT,
    kontak_pemesanan TEXT,
    jenis_kue TEXT,
    ukuran TEXT,
    deskripsi TEXT,
    tanggal_pesanan TEXT,
    tanggal_acara TEXT,
    status_pesanan TEXT CHECK(status_pesanan IN ('pending', 'diproses', 'selesai')),
    harga INTEGER
);

CREATE TABLE IF NOT EXISTS admin (
id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,    password TEXT NOT NULL
);