import os
import tempfile
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    uploaded_files = request.files.getlist("file[]")
    pdf_output = io.BytesIO()
    c = canvas.Canvas(pdf_output, pagesize=letter)

    ancho_pagina, alto_pagina = letter
    tamanio_maximo = 2 * 1024 * 1024  # 2 MB

    for uploaded_file in uploaded_files:
        try:
            image_data = uploaded_file.read()  # Leer datos binarios de la imagen
            image = Image.open(io.BytesIO(image_data))  # Abrir la imagen usando Pillow

            # Comprimir la imagen si es necesario
            if len(image_data) > tamanio_maximo:
                image.thumbnail((ancho_pagina, alto_pagina))

            # Obtener el tamaño de la imagen después de la posible compresión
            ancho_imagen, alto_imagen = image.size

            # Calcular la posición para centrar la imagen en la página
            x = (ancho_pagina - ancho_imagen) / 2
            y = (alto_pagina - alto_imagen) / 2

            # Cargar la imagen en el canvas del PDF
            c.drawImage(image, x, y, width=ancho_imagen, height=alto_imagen)
            c.showPage()

        except Exception as e:
            print("Error processing image:", e)
            continue

    c.save()
    pdf_output.seek(0)

    # Crear un archivo temporal seguro para el PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_filename = temp_file.name
        temp_file.write(pdf_output.getvalue())

    # Enviar el archivo PDF como respuesta en línea y eliminar el archivo temporal después de ser servido
    return send_file(temp_filename, as_attachment=False, download_name='resultado.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
