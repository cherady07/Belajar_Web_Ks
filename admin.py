from werkzeug.security import generate_password_hash
import sqlite3

# Ganti sesuai keinginan kamu / kakak kamu
username = "admin"
password_asli = "admin12345"

# Hash password-nya (ini yang akan disimpan, BUKAN password asli)
hashed = generate_password_hash(password_asli)

conn = sqlite3.connect('database.db')
conn.execute(
    'INSERT INTO admin (username, password) VALUES (?, ?)',
    (username, hashed)
)
conn.commit()  # WAJIB dipanggil setelah INSERT/UPDATE/DELETE, biar perubahan beneran tersimpan permanen
conn.close()

print("Akun admin berhasil dibuat!")