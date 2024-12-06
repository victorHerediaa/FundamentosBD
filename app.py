import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import pymysql

app = Flask(__name__)

# Configuración para el manejo de archivos
app.config['UPLOAD_FOLDER'] = 'uploads'  # Carpeta donde se guardarán las imágenes
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}  # Extensiones permitidas

# Verificar si el archivo tiene una extensión permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Conexión a la base de datos
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',  # Asegúrate de usar el usuario correcto
        password='victorandrey1',  # lLa contraseña de tu usuario de MariaDB
        db='patrimonio_cultural',  # Base de datos de tu proyecto
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Ruta principal para ver las piezas y agregar una nueva
@app.route('/', methods=['GET', 'POST'])
def index():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM piezas_patron')
        piezas = cursor.fetchall()
    connection.close()

    if request.method == 'POST':
        # Subir la imagen
        file = request.files['imagen']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Obtener los datos del formulario
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            anio = int(request.form['anio'])
            tipo = request.form['tipo']
            ubicacion = request.form['ubicacion']
            imagen = filename  # Guardamos el nombre del archivo de imagen

            # Conectar a la base de datos para insertar la pieza
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO piezas_patron (nombre, descripcion, anio, tipo, ubicacion, imagen)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nombre, descripcion, anio, tipo, ubicacion, imagen))
                connection.commit()
            connection.close()
            return redirect(url_for('index'))

    return render_template('index.html', piezas=piezas)

# Ruta para eliminar una pieza
@app.route('/eliminar_pieza/<int:id>', methods=['POST'])
def eliminar_pieza(id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Eliminar la pieza de la base de datos
        cursor.execute("DELETE FROM piezas_patron WHERE id = %s", (id,))
        connection.commit()
    connection.close()

    return redirect(url_for('index'))

# Ruta para servir las imágenes desde la carpeta uploads
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
