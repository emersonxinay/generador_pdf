import os
import tempfile
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import Flask, request, render_template, send_file, url_for

app = Flask(__name__)

# Función para procesar imágenes y generar el PDF
def generar_pdf(imagenes):
    pdf_output = tempfile.mktemp(suffix=".pdf")
    c = canvas.Canvas(pdf_output, pagesize=letter)

    ancho_pagina, alto_pagina = letter

    try:
        for idx, imagen in enumerate(imagenes):
            # Procesar la imagen y guardarla temporalmente
            temp_image_path = tempfile.mktemp(suffix=".png")
            imagen.save(temp_image_path)

            # Obtener el tamaño de la imagen después de la posible compresión
            ancho_imagen, alto_imagen = imagen.size
            x = (ancho_pagina - ancho_imagen) / 2
            y = (alto_pagina - alto_imagen) / 2

            # Cargar la imagen en el canvas del PDF
            c.drawImage(temp_image_path, x, y, width=ancho_imagen, height=alto_imagen)
            c.showPage()

            # Eliminar la imagen temporal después de procesarla
            os.remove(temp_image_path)

        c.save()
        return pdf_output  # Devolver la ruta del archivo PDF
    except Exception as e:
        print("Error al generar el PDF:", e)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        # Obtener las imágenes desde la solicitud (request)
        imagenes = []
        for uploaded_file in request.files.getlist("file[]"):
            image = Image.open(uploaded_file)
            imagenes.append(image)

        # Generar el PDF
        pdf_path = generar_pdf(imagenes)

        if pdf_path:
            # Obtener la URL del PDF temporal usando url_for
            pdf_url = url_for('static', filename=os.path.basename(pdf_path))

            # Enviar la URL del PDF como respuesta
            return render_template('index.html', pdf_url=pdf_url)
        else:
            return "Error al generar el PDF", 500
    except Exception as e:
        print("Error:", e)
        return "Error al procesar las imágenes", 500

if __name__ == '__main__':
    app.run(debug=True)
