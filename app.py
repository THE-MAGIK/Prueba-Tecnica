"""
Analizador de archivos (imagen o video) con Google Gemini y Flask.

- Permite subir imágenes o videos desde una página web.
- Usa la API de Google Gemini para analizar:
    * Imágenes → identifica producto, marca, uso, contenido sensible/prohibido.
    * Videos → detecta contenido sensible/prohibido y datos personales.
- Devuelve un archivo JSON con los resultados del análisis.
"""

import os
import json
import time
from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# --- Configuración inicial ---
load_dotenv()  # Cargar variables de entorno desde .env
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("No se encontró la GOOGLE_API_KEY.")
genai.configure(api_key=api_key)  # Configurar librería de Gemini

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'  # Carpeta temporal para guardar archivos
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Modelos de Gemini usados para imagen y video
image_model = genai.GenerativeModel('gemini-1.5-flash')
video_model = genai.GenerativeModel('gemini-1.5-flash')


# --- Funciones de análisis con Gemini ---

def analyze_image_with_ia(file_path: str):
    """
    Analiza una imagen con Gemini y devuelve un diccionario JSON
    con: contenido prohibido, información sensible,
    nombre, marca y descripción de uso del producto.
    """
    prompt = """
    Analiza la imagen y devuelve un JSON con:
    "contenido_prohibido", "informacion_sensible",
    "nombre_producto", "marca_producto", "descripcion_uso".
    Si no se puede determinar un campo, usar "No determinado".
    """
    uploaded_file = genai.upload_file(path=file_path, display_name="Análisis de Producto")
    response = image_model.generate_content(
        [prompt, uploaded_file],
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)


def analyze_video_with_ia(file_path):
    """
    Analiza un video con Gemini y devuelve un diccionario JSON
    con banderas de contenido sensible (obsceno, racista, personal, etc.)
    y también nombre, marca y descripción del producto.
    """
    prompt = """
    Analiza este video y devuelve un JSON con:
    - "tiene_contenido_obsceno"
    - "tiene_contenido_racista"
    - "tiene_informacion_personal"
    - "tiene_contenido_sensible_general"
    - "nombre_producto"
    - "marca_producto"
    - "descripcion_uso"
    """
    video_file = genai.upload_file(path=file_path, display_name="Análisis de Video")

    # Esperar a que el procesamiento termine
    while video_file.state.name == "PROCESSING":
        time.sleep(10)
        video_file = genai.get_file(video_file.name)
    if video_file.state.name == "FAILED":
        raise ValueError("El procesamiento del video falló.")

    response = video_model.generate_content(
        [prompt, video_file],
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)


# --- Rutas de la aplicación web ---

@app.route('/')
def index():
    """Muestra la página principal para subir archivos."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Maneja la subida y análisis de un archivo.
    - Detecta si es imagen o video.
    - Llama a la IA correspondiente.
    - Devuelve un JSON descargable con los resultados.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in ['.png', '.jpg', '.jpeg', '.webp']:
            analysis_type = "imagen"
            result = analyze_image_with_ia(file_path)
        elif file_ext in ['.mp4', '.mov', '.avi', '.mkv']:
            analysis_type = "video"
            result = analyze_video_with_ia(file_path)
        else:
            return jsonify({"error": "Formato de archivo no soportado"}), 400

        final_output = {
            "tipo_analisis": analysis_type,
            "nombre_archivo": filename,
            "resultado": result
        }
        response = jsonify(final_output)
        response.headers['Content-Disposition'] = f'attachment; filename=resultado_{os.path.splitext(filename)[0]}.json'
        return response

    except genai.types.generation_types.BlockedPromptException:
        return jsonify({"error": "El contenido fue bloqueado por políticas de seguridad."}), 400
    except Exception as e:
        error_str = str(e)
        if "API_KEY" in error_str or "permission" in error_str.lower():
            error_message = "Error de autenticación con Google: revisa tu API Key y configuración."
        else:
            error_message = f"Error interno: {error_str}"
        return jsonify({"error": error_message}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


# --- Punto de entrada ---
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
