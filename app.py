from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
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
    semua_menu = conn.execute('SELECT * FROM menu').fetchall()
    conn.close()

    sukses = request.args.get('sukses')
    nama = request.args.get('nama', 'Kak')

    return render_template('index.html', menu=semua_menu, sukses=sukses, nama=nama)



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

if __name__ == '__main__':
    app.run(debug=True)