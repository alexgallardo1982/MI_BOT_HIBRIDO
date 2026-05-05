import sqlite3
from datetime import datetime

def crear_tabla():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id TEXT,
            usuario_nombre TEXT,
            mensaje TEXT,
            respuesta TEXT,
            tipo TEXT,
            fecha TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def guardar_conversacion(usuario_id, usuario_nombre, mensaje, respuesta, tipo):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mensajes 
        (usuario_id, usuario_nombre, mensaje, respuesta, tipo, fecha)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (usuario_id, usuario_nombre, mensaje, respuesta, tipo, datetime.now()))
    conn.commit()
    conn.close()

def obtener_estadisticas():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM mensajes')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT tipo, COUNT(*) FROM mensajes GROUP BY tipo')
    por_tipo = cursor.fetchall()
    conn.close()
    return {'total': total, 'por_tipo': por_tipo}

crear_tabla()
