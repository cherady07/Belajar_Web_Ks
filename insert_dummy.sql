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

INSERT INTO bahan_baku (nama, harga_per_satuan, satuan) VALUES
('Tepung Terigu', 12000, 'kg'),
('Sosis', 35000, 'kg'),
('Minyak Goreng', 18000, 'liter'),
('Tusuk Sate', 15000, 'pack (isi 100)');

-- Asumsi id bahan_baku otomatis: 1=Tepung, 2=Sosis, 3=Minyak, 4=Tusuk
INSERT INTO resep (menu_id, bahan_baku_id, jumlah_dipakai) VALUES
(1, 1, 0.05),   -- Corndog Original pakai 0.05 kg (50gr) tepung
(1, 2, 0.08),   -- pakai 0.08 kg (80gr) sosis
(1, 3, 0.02),   -- pakai 0.02 liter minyak
(1, 4, 0.01),  -- pakai 0.01 pack (1 dari 100) tusuk sate

(2, 1, 0.05),
(2, 3, 0.08),
(2, 4, 0.02),
(2, 5, 0.01),
(2, 8, 0.03);