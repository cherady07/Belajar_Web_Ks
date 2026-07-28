-- ============================
-- Data dummy tabel: menu
-- ============================
INSERT INTO menu (nama, harga, stok, kategori, foto) VALUES
('Corndog Original', 15000, 20, 'corndog', 'corndog_original.png'),
('Corndog Keju', 18000, 15, 'corndog', 'corndog_keju.png'),
('Es Teh Manis', 5000, 30, 'minuman', 'es_teh.png'),
('Es Jeruk', 8000, 20, 'minuman', 'es_jeruk.png'),
('Dimsum Ayam', 15000, 15, 'dimsum', 'dimsum_ayam.png'),
('Dimsum Udang', 18000, 12, 'dimsum', 'dimsum_udang.png');
-- ============================
-- Data dummy tabel: daftar_harga
-- ============================
INSERT INTO daftar_harga (jenis_kue, ukuran, harga) VALUES
('Brownies', '20x20', 65000),
('Brownies', '22x22', 85000),
('Brownies', '24x24', 105000),
('Tart', 'Diameter 16cm', 120000),
('Tart', 'Diameter 20cm', 175000),
('Tart', 'Diameter 24cm', 250000);


-- ============================
-- Data dummy tabel: pesanan_custom
-- ============================
INSERT INTO pesanan_custom
(nama_pemesan, kontak_pemesanan, jenis_kue, ukuran, deskripsi, tanggal_pesanan, tanggal_acara, status_pesanan, harga)
VALUES
('Siti Rahma', '628123456789', 'Kue Ulang Tahun', NULL, 'Tema Frozen, warna biru-putih, tulisan Happy Birthday Nadia', '2026-07-20', '2026-07-28', 'diproses', 250000),
('Budi Santoso', '628987654321', 'Brownies', '22x22', 'Brownies polos tanpa topping tambahan', '2026-07-22', '2026-07-25', 'selesai', 85000),
('Ayu Lestari', '628112233445', 'Kue Wisuda', NULL, 'Topper nama Ayu S.Kom, warna hijau toga', '2026-07-24', '2026-08-02', 'pending', NULL),
('Doni Prasetyo', '628556677889', 'Tart', 'Diameter 20cm', 'Tart coklat dengan tulisan Selamat Melamar', '2026-07-25', '2026-07-30', 'pending', 175000);

