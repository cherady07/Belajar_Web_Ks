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
    semua_menu = conn.execute('SELECT * FROM menu').fetchall()  # 2 method: 1) jalankan query, 2) ambil semua hasilnya
    conn.close()
    return render_template('index.html', menu=semua_menu)  # kirim data menu ke template



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

if __name__ == '__main__':
    app.run(debug=True)