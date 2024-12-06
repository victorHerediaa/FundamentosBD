import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Función para conectarse a la base de datos
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

# Ruta principal para mostrar las piezas
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM piezas_patron;')  # Ajusta el nombre de la tabla según tu caso
    piezas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', piezas=piezas)

# Ruta para agregar una nueva pieza
@app.route('/insertar_pieza', methods=['POST'])
def insertar_pieza():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        anio = request.form['anio']
        tipo = request.form['tipo']
        ubicacion = request.form['ubicacion']

        # Agregar la nueva pieza a la base de datos
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO piezas_patron (nombre, descripcion, anio, tipo, ubicacion)
                    VALUES (%s, %s, %s, %s, %s)''', 
                    (nombre, descripcion, anio, tipo, ubicacion))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('index'))

# Ruta para eliminar una pieza
@app.route('/eliminar_pieza/<int:id>', methods=['GET'])
def eliminar_pieza(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM piezas_patron WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

# Iniciar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
