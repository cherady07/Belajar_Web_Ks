from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from datetime import datetime  # tambahin di import, ganti baris 'from datetime import date' jadi ini kalau belum ada
import sqlite3  # library Python bawaan buat koneksi ke SQLite (sudah dibahas sebelumnya)
import os


app = Flask(__name__)
app.secret_key = 'ganti_dengan_teks_acak_apa_saja_yang_rahasia'


def get_db_connection():
    conn = sqlite3.connect('database.db')  # nama file database kamu
    conn.row_factory = sqlite3.Row  # biar hasil query bisa diakses kayak dictionary (pakai nama kolom), bukan cuma index angka
    return conn

@app.route('/')
def home():
    conn = get_db_connection()

    sekarang = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    diskon_aktif = conn.execute('''
        SELECT * FROM diskon
        WHERE status_aktif = 1 AND tanggal_mulai <= ? AND tanggal_selesai >= ?
    ''', (sekarang, sekarang)).fetchall()
    diskon_by_menu = {d['menu_id']: d for d in diskon_aktif}

    menu_baru = conn.execute('''
        SELECT menu.* FROM pengumuman_menu_baru
        JOIN menu ON pengumuman_menu_baru.menu_id = menu.id
        WHERE pengumuman_menu_baru.status_aktif = 1
          AND pengumuman_menu_baru.tanggal_mulai <= ?
          AND pengumuman_menu_baru.tanggal_selesai >= ?
    ''', (sekarang, sekarang)).fetchall()
    id_menu_baru = [item['id'] for item in menu_baru]

    if id_menu_baru:
        placeholder = ','.join('?' * len(id_menu_baru))
        semua_menu = conn.execute(
            f'SELECT * FROM menu WHERE id NOT IN ({placeholder})', id_menu_baru
        ).fetchall()
    else:
        semua_menu = conn.execute('SELECT * FROM menu').fetchall()

    ide_voting = conn.execute('''
        SELECT ide_menu.*, COUNT(vote.id) AS jumlah_vote
        FROM ide_menu
        LEFT JOIN vote ON ide_menu.id = vote.ide_menu_id
        WHERE ide_menu.status_tampil = 1
          AND ide_menu.tanggal_mulai_tampil <= ?
          AND ide_menu.tanggal_selesai_tampil >= ?
        GROUP BY ide_menu.id
        ORDER BY jumlah_vote DESC
    ''', (sekarang, sekarang)).fetchall()

    conn.close()

    sukses = request.args.get('sukses')
    nama = request.args.get('nama', 'Kak')
    vote_pesan = request.args.get('vote_pesan')

    return render_template('index.html', menu=semua_menu, diskon_by_menu=diskon_by_menu,
                            menu_baru=menu_baru, ide_voting=ide_voting,
                            sukses=sukses, nama=nama, vote_pesan=vote_pesan)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        admin = conn.execute(
            'SELECT * FROM admin WHERE username = ?', (username,)
        ).fetchone()
        conn.close()

        if admin and check_password_hash(admin['password'], password):
            session['admin_logged_in'] = True
            session['username'] = admin['username']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Username atau password salah')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    semua_menu = conn.execute('SELECT * FROM menu').fetchall()
    conn.close()

    return render_template('menu/dashboard.html', menu=semua_menu, username=session['username'])
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/tambah-menu', methods=['GET', 'POST'])
def tambah_menu():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        stok = request.form['stok']
        kategori = request.form['kategori']
        foto = request.files['foto']

        # simpan file foto ke folder static/images/menu/
        nama_file = foto.filename
        foto.save(os.path.join('static/images/menu', nama_file))

        # simpan datanya ke database
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO menu (nama, harga, stok, kategori, foto) VALUES (?, ?, ?, ?, ?)',
            (nama, harga, stok, kategori, nama_file)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('menu/tambah_menu.html')

@app.route('/edit-menu/<int:id>', methods=['GET', 'POST'])
def edit_menu(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    item = conn.execute('SELECT * FROM menu WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        stok = request.form['stok']
        kategori = request.form['kategori']
        foto = request.files['foto']

        # cek apakah admin upload foto baru atau tidak
        if foto and foto.filename != '':
            nama_file = foto.filename
            foto.save(os.path.join('static/images/menu', nama_file))
        else:
            nama_file = item['foto']  # tetap pakai foto lama

        conn.execute(
            'UPDATE menu SET nama = ?, harga = ?, stok = ?, kategori = ?, foto = ? WHERE id = ?',
            (nama, harga, stok, kategori, nama_file, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('menu/edit_menu.html', item=item)


@app.route('/hapus-menu/<int:id>')
def hapus_menu(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM menu WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/kelola-pesanan')
def kelola_pesanan():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    semua_pesanan = conn.execute(
        'SELECT * FROM pesanan_custom ORDER BY tanggal_pesanan DESC'
    ).fetchall()
    conn.close()

    return render_template('pesanan/kelola_pesanan.html', pesanan=semua_pesanan, username=session['username'])

@app.route('/edit-pesanan/<int:id>', methods=['GET', 'POST'])
def edit_pesanan(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    pesanan = conn.execute('SELECT * FROM pesanan_custom WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        nama_pemesan = request.form['nama_pemesan']
        kontak_pemesanan = request.form['kontak_pemesanan']
        jenis_kue = request.form['jenis_kue']
        ukuran = request.form['ukuran']
        deskripsi = request.form['deskripsi']
        tanggal_acara = request.form['tanggal_acara']
        status_pesanan = request.form['status_pesanan']
        harga = request.form['harga']

        # kalau ukuran/harga dikosongkan, simpan sebagai NULL, bukan string kosong
        ukuran = ukuran if ukuran else None
        harga = harga if harga else None

        conn.execute('''
            UPDATE pesanan_custom
            SET nama_pemesan = ?, kontak_pemesanan = ?, jenis_kue = ?, ukuran = ?,
                deskripsi = ?, tanggal_acara = ?, status_pesanan = ?, harga = ?
            WHERE id = ?
        ''', (nama_pemesan, kontak_pemesanan, jenis_kue, ukuran, deskripsi,
              tanggal_acara, status_pesanan, harga, id))
        conn.commit()
        conn.close()
        return redirect(url_for('kelola_pesanan'))

    conn.close()
    return render_template('pesanan/edit_pesanan.html', p=pesanan)

from datetime import date  # tambahin di baris import paling atas

@app.route('/pesan-custom', methods=['POST'])
def pesan_custom():
    nama_pemesan = request.form['nama_pemesan']
    kontak_pemesanan = request.form['kontak_pemesanan']
    jenis_kue = request.form['jenis_kue']
    ukuran = request.form['ukuran']
    deskripsi = request.form['deskripsi']
    tanggal_acara = request.form['tanggal_acara']

    ukuran = ukuran if ukuran else None
    tanggal_pesanan = date.today().isoformat()

    # tangani upload foto referensi (opsional)
    foto = request.files['foto_referensi']
    if foto and foto.filename != '':
        nama_file_foto = foto.filename
        foto.save(os.path.join('static/images/referensi', nama_file_foto))
    else:
        nama_file_foto = None

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO pesanan_custom
        (nama_pemesan, kontak_pemesanan, jenis_kue, ukuran, deskripsi, tanggal_pesanan, tanggal_acara, status_pesanan, harga, foto_referensi)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', NULL, ?)
    ''', (nama_pemesan, kontak_pemesanan, jenis_kue, ukuran, deskripsi, tanggal_pesanan, tanggal_acara, nama_file_foto))
    conn.commit()
    conn.close()

    session['last_order_name'] = nama_pemesan
    return redirect(url_for('home', sukses=1, nama=nama_pemesan))

@app.route('/daftar-harga')
def daftar_harga():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    semua_harga = conn.execute('SELECT * FROM daftar_harga').fetchall()
    conn.close()

    return render_template('harga/daftar_harga.html', harga=semua_harga, username=session['username'])


@app.route('/tambah-harga', methods=['GET', 'POST'])
def tambah_harga():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        jenis_kue = request.form['jenis_kue']
        ukuran = request.form['ukuran']
        harga = request.form['harga']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO daftar_harga (jenis_kue, ukuran, harga) VALUES (?, ?, ?)',
            (jenis_kue, ukuran, harga)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('daftar_harga'))

    return render_template('harga/tambah_harga.html')


@app.route('/edit-harga/<int:id>', methods=['GET', 'POST'])
def edit_harga(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    item = conn.execute('SELECT * FROM daftar_harga WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        jenis_kue = request.form['jenis_kue']
        ukuran = request.form['ukuran']
        harga = request.form['harga']

        conn.execute(
            'UPDATE daftar_harga SET jenis_kue = ?, ukuran = ?, harga = ? WHERE id = ?',
            (jenis_kue, ukuran, harga, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('daftar_harga'))

    conn.close()
    return render_template('harga/edit_harga.html', item=item)


@app.route('/hapus-harga/<int:id>')
def hapus_harga(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM daftar_harga WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('daftar_harga'))

@app.route('/bahan-baku')
def bahan_baku():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    semua_bahan = conn.execute('SELECT * FROM bahan_baku').fetchall()
    conn.close()
    return render_template('hpp/bahan_baku.html', bahan=semua_bahan, username=session['username'])


@app.route('/tambah-bahan', methods=['GET', 'POST'])
def tambah_bahan():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nama = request.form['nama']
        harga_per_satuan = request.form['harga_per_satuan']
        satuan = request.form['satuan']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO bahan_baku (nama, harga_per_satuan, satuan) VALUES (?, ?, ?)',
            (nama, harga_per_satuan, satuan)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('bahan_baku'))

    return render_template('hpp/tambah_bahan.html')


@app.route('/edit-bahan/<int:id>', methods=['GET', 'POST'])
def edit_bahan(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    item = conn.execute('SELECT * FROM bahan_baku WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        nama = request.form['nama']
        harga_per_satuan = request.form['harga_per_satuan']
        satuan = request.form['satuan']

        conn.execute(
            'UPDATE bahan_baku SET nama = ?, harga_per_satuan = ?, satuan = ? WHERE id = ?',
            (nama, harga_per_satuan, satuan, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('bahan_baku'))

    conn.close()
    return render_template('hpp/edit_bahan.html', item=item)


@app.route('/hapus-bahan/<int:id>')
def hapus_bahan(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM bahan_baku WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('bahan_baku'))

@app.route('/hpp')
def hpp():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    hasil_hpp = conn.execute('''
        SELECT menu.id, menu.nama, menu.harga AS harga_jual,
               SUM(bahan_baku.harga_per_satuan * resep.jumlah_dipakai) AS total_hpp
        FROM resep
        JOIN menu ON resep.menu_id = menu.id
        JOIN bahan_baku ON resep.bahan_baku_id = bahan_baku.id
        GROUP BY menu.id
    ''').fetchall()
    conn.close()

    return render_template('hpp/hpp.html', hpp=hasil_hpp, username=session['username'])  # <- cuma ini yang berubah, tambahin prefix 'hpp/'

@app.route('/resep')
def resep():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    semua_resep = conn.execute('''
        SELECT resep.id, menu.nama AS nama_menu, bahan_baku.nama AS nama_bahan,
               resep.jumlah_dipakai, bahan_baku.satuan
        FROM resep
        JOIN menu ON resep.menu_id = menu.id
        JOIN bahan_baku ON resep.bahan_baku_id = bahan_baku.id
        ORDER BY menu.nama
    ''').fetchall()
    conn.close()
    return render_template('hpp/resep.html', resep=semua_resep, username=session['username'])


@app.route('/tambah-resep', methods=['GET', 'POST'])
def tambah_resep():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        menu_id = request.form['menu_id']
        bahan_baku_id = request.form['bahan_baku_id']
        jumlah_dipakai = request.form['jumlah_dipakai']

        conn.execute(
            'INSERT INTO resep (menu_id, bahan_baku_id, jumlah_dipakai) VALUES (?, ?, ?)',
            (menu_id, bahan_baku_id, jumlah_dipakai)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('resep'))

    daftar_menu = conn.execute('SELECT id, nama FROM menu').fetchall()
    daftar_bahan = conn.execute('SELECT id, nama, satuan FROM bahan_baku').fetchall()
    conn.close()
    return render_template('hpp/tambah_resep.html', daftar_menu=daftar_menu, daftar_bahan=daftar_bahan)


@app.route('/hapus-resep/<int:id>')
def hapus_resep(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM resep WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('resep'))

@app.route('/edit-resep/<int:id>', methods=['GET', 'POST'])
def edit_resep(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    item = conn.execute('SELECT * FROM resep WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        menu_id = request.form['menu_id']
        bahan_baku_id = request.form['bahan_baku_id']
        jumlah_dipakai = request.form['jumlah_dipakai']

        conn.execute(
            'UPDATE resep SET menu_id = ?, bahan_baku_id = ?, jumlah_dipakai = ? WHERE id = ?',
            (menu_id, bahan_baku_id, jumlah_dipakai, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('resep'))

    daftar_menu = conn.execute('SELECT id, nama FROM menu').fetchall()
    daftar_bahan = conn.execute('SELECT id, nama, satuan FROM bahan_baku').fetchall()
    conn.close()
    return render_template('hpp/edit_resep.html', item=item, daftar_menu=daftar_menu, daftar_bahan=daftar_bahan)

@app.route('/diskon')
def diskon():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    semua_diskon = conn.execute('''
        SELECT diskon.*, menu.nama AS nama_menu, menu.harga AS harga_asli
        FROM diskon
        JOIN menu ON diskon.menu_id = menu.id
        ORDER BY diskon.tanggal_mulai DESC
    ''').fetchall()
    conn.close()
    return render_template('promo/diskon.html', diskon=semua_diskon, username=session['username'])


@app.route('/tambah-diskon', methods=['GET', 'POST'])
def tambah_diskon():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        menu_id = request.form['menu_id']
        persentase_diskon = request.form['persentase_diskon']
        tanggal_mulai = request.form['tanggal_mulai'].replace('T', ' ') + ':00'
        tanggal_selesai = request.form['tanggal_selesai'].replace('T', ' ') + ':00'
        status_aktif = 1 if request.form.get('status_aktif') else 0

        conn.execute(
            'INSERT INTO diskon (menu_id, persentase_diskon, tanggal_mulai, tanggal_selesai, status_aktif) VALUES (?, ?, ?, ?, ?)',
            (menu_id, persentase_diskon, tanggal_mulai, tanggal_selesai, status_aktif)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('diskon'))

    daftar_menu = conn.execute('SELECT id, nama FROM menu').fetchall()
    conn.close()
    return render_template('promo/tambah_diskon.html', daftar_menu=daftar_menu)


@app.route('/edit-diskon/<int:id>', methods=['GET', 'POST'])
def edit_diskon(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    item = conn.execute('SELECT * FROM diskon WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        menu_id = request.form['menu_id']
        persentase_diskon = request.form['persentase_diskon']
        tanggal_mulai = request.form['tanggal_mulai'].replace('T', ' ') + ':00'
        tanggal_selesai = request.form['tanggal_selesai'].replace('T', ' ') + ':00'
        status_aktif = 1 if request.form.get('status_aktif') else 0

        conn.execute(
            'UPDATE diskon SET menu_id = ?, persentase_diskon = ?, tanggal_mulai = ?, tanggal_selesai = ?, status_aktif = ? WHERE id = ?',
            (menu_id, persentase_diskon, tanggal_mulai, tanggal_selesai, status_aktif, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('diskon'))

    daftar_menu = conn.execute('SELECT id, nama FROM menu').fetchall()
    conn.close()
    return render_template('promo/edit_diskon.html', item=item, daftar_menu=daftar_menu)


@app.route('/hapus-diskon/<int:id>')
def hapus_diskon(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM diskon WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('diskon'))

@app.route('/pengumuman')
def pengumuman():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    semua_pengumuman = conn.execute('''
        SELECT pengumuman_menu_baru.*, menu.nama AS nama_menu, menu.foto AS foto_menu
        FROM pengumuman_menu_baru
        JOIN menu ON pengumuman_menu_baru.menu_id = menu.id
        ORDER BY pengumuman_menu_baru.tanggal_mulai DESC
    ''').fetchall()
    conn.close()
    return render_template('promo/pengumuman.html', pengumuman=semua_pengumuman, username=session['username'])

@app.route('/tambah-pengumuman', methods=['GET', 'POST'])
def tambah_pengumuman():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        menu_id = request.form['menu_id']
        tanggal_mulai = request.form['tanggal_mulai'].replace('T', ' ') + ':00'
        tanggal_selesai = request.form['tanggal_selesai'].replace('T', ' ') + ':00'
        status_aktif = 1 if request.form.get('status_aktif') else 0

        conn.execute(
            'INSERT INTO pengumuman_menu_baru (menu_id, tanggal_mulai, tanggal_selesai, status_aktif) VALUES (?, ?, ?, ?)',
            (menu_id, tanggal_mulai, tanggal_selesai, status_aktif)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('pengumuman'))

    daftar_menu = conn.execute('SELECT id, nama FROM menu').fetchall()
    conn.close()
    return render_template('promo/tambah_pengumuman.html', daftar_menu=daftar_menu)


@app.route('/edit-pengumuman/<int:id>', methods=['GET', 'POST'])
def edit_pengumuman(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    item = conn.execute('SELECT * FROM pengumuman_menu_baru WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        menu_id = request.form['menu_id']
        tanggal_mulai = request.form['tanggal_mulai'].replace('T', ' ') + ':00'
        tanggal_selesai = request.form['tanggal_selesai'].replace('T', ' ') + ':00'
        status_aktif = 1 if request.form.get('status_aktif') else 0

        conn.execute(
            'UPDATE pengumuman_menu_baru SET menu_id = ?, tanggal_mulai = ?, tanggal_selesai = ?, status_aktif = ? WHERE id = ?',
            (menu_id, tanggal_mulai, tanggal_selesai, status_aktif, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('pengumuman'))

    daftar_menu = conn.execute('SELECT id, nama FROM menu').fetchall()
    conn.close()
    return render_template('promo/edit_pengumuman.html', item=item, daftar_menu=daftar_menu)


@app.route('/hapus-pengumuman/<int:id>')
def hapus_pengumuman(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM pengumuman_menu_baru WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('pengumuman'))

@app.route('/ide-menu')
def ide_menu():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    semua_ide = conn.execute('''
        SELECT ide_menu.*, COUNT(vote.id) AS jumlah_vote
        FROM ide_menu
        LEFT JOIN vote ON ide_menu.id = vote.ide_menu_id
        GROUP BY ide_menu.id
        ORDER BY jumlah_vote DESC
    ''').fetchall()

    sekarang = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sedang_voting = conn.execute('''
        SELECT ide_menu.*, COUNT(vote.id) AS jumlah_vote
        FROM ide_menu
        LEFT JOIN vote ON ide_menu.id = vote.ide_menu_id
        WHERE ide_menu.status_tampil = 1
          AND ide_menu.tanggal_mulai_tampil <= ?
          AND ide_menu.tanggal_selesai_tampil >= ?
        GROUP BY ide_menu.id
        ORDER BY jumlah_vote DESC
    ''', (sekarang, sekarang)).fetchall()
    conn.close()

    return render_template('promo/ide_menu.html', ide=semua_ide, sedang_voting=sedang_voting, username=session['username'])

@app.route('/tambah-ide', methods=['GET', 'POST'])
def tambah_ide():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nama_ide = request.form['nama_ide']
        deskripsi = request.form['deskripsi']
        tanggal_diajukan = date.today().isoformat()
        status_tampil = 1 if request.form.get('status_tampil') else 0

        foto = request.files['foto']
        if foto and foto.filename != '':
            nama_file_foto = foto.filename
            foto.save(os.path.join('static/images/ide_menu', nama_file_foto))
        else:
            nama_file_foto = None

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO ide_menu (nama_ide, deskripsi, tanggal_diajukan, foto, status_tampil) VALUES (?, ?, ?, ?, ?)',
            (nama_ide, deskripsi, tanggal_diajukan, nama_file_foto, status_tampil)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('ide_menu'))

    return render_template('promo/tambah_ide.html')


@app.route('/hapus-ide/<int:id>')
def hapus_ide(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM ide_menu WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('ide_menu'))

@app.route('/edit-ide/<int:id>', methods=['GET', 'POST'])
def edit_ide(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    item = conn.execute('SELECT * FROM ide_menu WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        nama_ide = request.form['nama_ide']
        deskripsi = request.form['deskripsi']
        status_tampil = 1 if request.form.get('status_tampil') else 0

        foto = request.files['foto']
        if foto and foto.filename != '':
            nama_file_foto = foto.filename
            foto.save(os.path.join('static/images/ide_menu', nama_file_foto))
        else:
            nama_file_foto = item['foto']

        conn.execute(
            'UPDATE ide_menu SET nama_ide = ?, deskripsi = ?, foto = ?, status_tampil = ? WHERE id = ?',
            (nama_ide, deskripsi, nama_file_foto, status_tampil, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('ide_menu'))

    conn.close()
    return render_template('promo/edit_ide.html', item=item)

@app.route('/mulai-voting', methods=['POST'])
def mulai_voting():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    ide_terpilih = request.form.getlist('ide_ids')
    tanggal_mulai = request.form['tanggal_mulai_voting'].replace('T', ' ') + ':00'
    tanggal_selesai = request.form['tanggal_selesai_voting'].replace('T', ' ') + ':00'

    conn = get_db_connection()
    for id_ide in ide_terpilih:
        # hapus vote lama, mulai dari 0 lagi
        conn.execute('DELETE FROM vote WHERE ide_menu_id = ?', (id_ide,))
        conn.execute(
            'UPDATE ide_menu SET status_tampil = 1, tanggal_mulai_tampil = ?, tanggal_selesai_tampil = ? WHERE id = ?',
            (tanggal_mulai, tanggal_selesai, id_ide)
        )
    conn.commit()
    conn.close()

    return redirect(url_for('ide_menu'))

@app.route('/hentikan-voting/<int:id>')
def hentikan_voting(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('UPDATE ide_menu SET status_tampil = 0 WHERE id = ?', (id,))

    # cek sisa ide yang masih aktif setelah yang ini dihentikan
    sisa_aktif = conn.execute(
        'SELECT id FROM ide_menu WHERE status_tampil = 1'
    ).fetchall()

    # kalau tinggal 1 ide aktif, otomatis hentikan juga (voting minimal butuh 2 pilihan)
    if len(sisa_aktif) == 1:
        conn.execute('UPDATE ide_menu SET status_tampil = 0 WHERE id = ?', (sisa_aktif[0]['id'],))

    conn.commit()
    conn.close()
    return redirect(url_for('ide_menu'))

@app.route('/hentikan-semua-voting')
def hentikan_semua_voting():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('UPDATE ide_menu SET status_tampil = 0 WHERE status_tampil = 1')
    conn.commit()
    conn.close()
    return redirect(url_for('ide_menu'))

@app.route('/vote', methods=['POST'])
def vote():
    ide_menu_id = request.form['ide_menu_id']
    nomor_wa = request.form['nomor_wa']
    tanggal_vote = date.today().isoformat()

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO vote (ide_menu_id, nomor_wa, tanggal_vote) VALUES (?, ?, ?)',
            (ide_menu_id, nomor_wa, tanggal_vote)
        )
        conn.commit()
        pesan = 'berhasil'
    except sqlite3.IntegrityError:
        pesan = 'sudah_vote'
    finally:
        conn.close()

    return redirect(url_for('home', vote_pesan=pesan) + '#voting')

if __name__ == '__main__':
    app.run(debug=True)