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

    return render_template('dashboard.html', menu=semua_menu, username=session['username'])
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

    return render_template('tambah_menu.html')

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
    return render_template('edit_menu.html', item=item)


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

    return render_template('kelola_pesanan.html', pesanan=semua_pesanan, username=session['username'])

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
    return render_template('edit_pesanan.html', p=pesanan)

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

if __name__ == '__main__':
    app.run(debug=True)