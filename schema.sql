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
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Tabel 1: daftar bahan baku yang ada
CREATE TABLE IF NOT EXISTS bahan_baku (
    id INTEGER PRIMARY KEY,
    nama TEXT NOT NULL,
    harga_per_satuan INTEGER NOT NULL,
    satuan TEXT NOT NULL
);

-- Tabel 2: tabel "penghubung" (junction table) - resep tiap menu
CREATE TABLE IF NOT EXISTS resep (
    id INTEGER PRIMARY KEY,
    menu_id INTEGER NOT NULL,
    bahan_baku_id INTEGER NOT NULL,
    jumlah_dipakai REAL NOT NULL,
    FOREIGN KEY (menu_id) REFERENCES menu(id),
    FOREIGN KEY (bahan_baku_id) REFERENCES bahan_baku(id)
);

CREATE TABLE IF NOT EXISTS diskon (
    id INTEGER PRIMARY KEY,
    menu_id INTEGER NOT NULL,
    persentase_diskon INTEGER NOT NULL,
    tanggal_mulai TEXT NOT NULL,
    tanggal_selesai TEXT NOT NULL,
    status_aktif INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (menu_id) REFERENCES menu(id)
);

CREATE TABLE IF NOT EXISTS pengumuman_menu_baru (
    id INTEGER PRIMARY KEY,
    menu_id INTEGER NOT NULL,
    tanggal_mulai TEXT NOT NULL,
    tanggal_selesai TEXT NOT NULL,
    status_aktif INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (menu_id) REFERENCES menu(id)
);

CREATE TABLE IF NOT EXISTS ide_menu (
    id INTEGER PRIMARY KEY,
    nama_ide TEXT NOT NULL,
    deskripsi TEXT,
    tanggal_diajukan TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vote (
    id INTEGER PRIMARY KEY,
    ide_menu_id INTEGER NOT NULL,
    nomor_wa TEXT NOT NULL,
    tanggal_vote TEXT NOT NULL,
    FOREIGN KEY (ide_menu_id) REFERENCES ide_menu(id),
    UNIQUE (ide_menu_id, nomor_wa)
);