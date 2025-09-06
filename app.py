# IMPORTACIONES NECESARIAS 
import os
import json
import time
from flask import Flask, request, render_template, jsonify      
import google.generativeai as genai
from werkzeug.utils import secure_filename
from dotenv import load_dotenv


# todo respecto a la key fue sacado de documentacion e implementado con IA a este codigo 

# Cargamos las variables de entorno del archivo .env.
load_dotenv()

# Obtenemos la API Key de las variables de entorno que acabamos de cargar.
api_key = os.getenv("GOOGLE_API_KEY")

# Imprimimos los primeros 5 caracteres de la clave para confirmar que se cargó correctamente,
print(f"DEBUG: La API Key que se está usando comienza con: '{str(api_key)[:5]}...'")

# Si la API Key no se encuentra, detenemos la aplicación con un error claro.
if not api_key:
    raise ValueError("No se encontró la GOOGLE_API_KEY. Asegúrate de que tu archivo .env existe y está configurado correctamente.")

# Configuramos la librería de Google con nuestra clave. A partir de aquí,
# la librería `genai` sabrá cómo autenticarse en todas las llamadas.
genai.configure(api_key=api_key)

print("DEBUG: Configuración de la API Key completada.")

# Creamos la aplicación Flask.
app = Flask(__name__)

# Configuramos Flask para que no convierta caracteres no ASCII a secuencias de escape.
# Esto asegura que caracteres como 'ñ', 'á', 'é', etc., se muestren correctamente en el JSON.
app.config['JSON_AS_ASCII'] = False

# Definimos el nombre de la carpeta donde guardaremos temporalmente los archivos subidos.
UPLOAD_FOLDER = 'uploads'
# Nos aseguramos de que esta carpeta exista. Si no, la creamos.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Le decimos a Flask que use esta carpeta para las subidas.
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# se preparan los modelos de IA que se utilizaran, en este caso es el geminmi 1.5-flash ya que funciona muy bien para los dos
#se saco de documentacion de google generative ai
image_model = genai.GenerativeModel('gemini-1.5-flash')
video_model = genai.GenerativeModel('gemini-1.5-flash')



# aqui van los prompts y las funciones que llaman a la IA            


def analyze_image_with_ia(file_path: str):
    """
    Analiza una imagen utilizando la IA de Gemini.

    Args:
        file_path (str): La ruta local del archivo de imagen a analizar.

    Returns:
        dict: Un diccionario con los resultados del análisis.
    """
    # Este es el prompt que le di para imagenes


    #prompt Angelo
    prompt = """                                                    
    Analiza muy detalladamente la siguiente imagen y proporciona únicamente un objeto JSON con la siguiente clave:

        "contenido_prohibido": Si la imagen tiene contenido obsceno, violento, sexual, racista o cualquier tipo de
         contenido sensible explicar cual es con una respuesta muy puntual.

        "nombre_producto": El nombre comercial del producto.

        "marca_producto": La marca del producto.

        "informacion_sensible": Un listado con cualquier información sensible que aparezca en la imagen, como datos personales,
        documentos de identidad, direcciones, números de teléfono o información financiera etc.

        Si no puedes determinar alguno de los campos, déjalo como "No determinado".
        No incluyas nada más en tu respuesta, solo el JSON."""
    
    #Codigo IA
    # Primero, subimos el archivo a los servidores de Google. La API no trabaja
    # directamente con archivos locales, así que este paso es necesario.
    print(f"Subiendo y preparando la imagen: {file_path}")
    uploaded_file = genai.upload_file(path=file_path, display_name="Análisis de Producto")
    
    # Ahora sí, le pedimos al modelo que genere el contenido. Le pasamos dos cosas:
    # 1. el prompt
    # 2. El archivo que acabamos de subir.
    # También le indicamos que queremos la respuesta en formato JSON.
    #Codigo IA
    response = image_model.generate_content(
        [prompt, uploaded_file],
        generation_config={"response_mime_type": "application/json"}
    )

    # La respuesta de la IA viene como texto. Para asegurar que los caracteres especiales
    # se interpreten correctamente, primero se codifica a bytes y luego se decodifica
    # usando 'unicode_escape' antes de convertirlo a un objeto Python.
    return json.loads(response.text.encode('latin-1').decode('unicode_escape'))


    # Este es el prompt que le di para videos
def analyze_video_with_ia(file_path):
    """
    Analiza un video utilizando la IA de Gemini.

    Args:
        file_path (str): La ruta local del archivo de video a analizar.

    Returns:
        dict: Un diccionario con los resultados del análisis de moderación.
    """
    # Al igual que con la imagen, definimos un prompt muy específico para el video.
   

    #prompt Angelo
    prompt = """
    Actúa como un sistema de moderación de contenido. Analiza muy detalladamente este video y determina si contiene alguna de las siguientes categorías. 
    Responde únicamente con un objeto JSON con las siguientes claves:

        "contenido_prohibido": Si el video tiene contenido obsceno, violento, sexual, racista o cualquier tipo de
         contenido sensible, mostrar un listado de cada una y explicar cual es con una respuesta muy puntual.

        "nombre_producto": El nombre comercial del producto.

        "marca_producto": La marca del producto.

        "informacion_sensible": mostrar Un listado con cualquier información sensible que aparezca en la imagen, como datos personales,
        documentos de identidad, direcciones, números de teléfono o información financiera etc; Mostrar esa informacion.

    No incluyas nada más en tu respuesta, solo el JSON.
    """
    #Codigo IA
    # Subimos el archivo de video a los servidores de Google.
    print(f"Subiendo el archivo de video: {file_path}...")
    video_file = genai.upload_file(path=file_path, display_name="Análisis de Video")
    
    #Codigo IA
    # El procesamiento de video no es instantáneo. La API necesita tiempo para procesarlo.
    # Este bucle `while` se encarga de esperar. Cada 10 segundos, le preguntamos a la API:
    # Continuamos esperando hasta que el estado ya no sea "PROCESSING".
    while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    #condicional para ver si el procesamiento fallo
    if video_file.state.name == "FAILED":
        raise ValueError("El procesamiento del video falló.")
    
    #Codigo IA
    # Una vez que el video está listo, le pedimos al modelo que lo analice.
    print("\nVideo procesado. Generando contenido...")
    response = video_model.generate_content(
        [prompt, video_file],
        generation_config={"response_mime_type": "application/json"}
    )
    # La respuesta de la IA viene como texto. Para asegurar que los caracteres especiales
    # se interpreten correctamente, primero se codifica a bytes y luego se decodifica
    # usando 'unicode_escape' antes de convertirlo a un objeto Python.
    return json.loads(response.text.encode('latin-1').decode('unicode_escape'))

#  RUTAS DE LA APLICACIÓN WEB
#Codigo angelo
#Aqui llamamos al front 
@app.route('/')
def index():
    """Muestra la página principal para subir archivos."""
   
    # le mostramos el archivo 'index.html' que está en la carpeta 'templates'.
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Maneja la subida y análisis de un archivo (imagen o video).
    """
    print("Recibida solicitud de subida de archivo.")
    
    #Codigo Angelo
    # Primero, verificamos si la solicitud realmente contiene un archivo.
    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo"}), 400
    print("Archivo encontrado en la solicitud.")
    
    file = request.files['file']

    # Verificamos si el usuario seleccionó un archivo o si hizo clic en "subir" sin elegir nada.
    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400
    print("Archivo seleccionado:")
    
    #Codigo IA
    # Si todo va bien y tenemos un archivo entonces procedemos.
    if file:
        # Limpiamos el nombre del archivo para evitar problemas de seguridad.
        # Por ejemplo, si alguien sube un archivo llamado "../../etc/passwd",
        # `secure_filename` lo convertirá en "etc_passwd", evitando que se salga del directorio.
        filename = secure_filename(file.filename)
        print(f"Procesando archivo: {filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Determinar el tipo de archivo (imagen o video)
        file_ext = os.path.splitext(filename)[1].lower()
        result = {}
        analysis_type = ""
        print("Iniciando análisis con IA...")
        
        #Codigo IA
        try:
            if file_ext in ['.png', '.jpg', '.jpeg', '.webp']:
                analysis_type = "imagen"
                result = analyze_image_with_ia(file_path)
            elif file_ext in ['.mp4', '.mov', '.avi', '.mkv']:
                analysis_type = "video"
                result = analyze_video_with_ia(file_path)
            else:
                return jsonify({"error": "Formato de archivo no soportado"}), 400
            print("Análisis completado.")
            
            # Preparamos una respuesta y estructurada para el usuario.
            final_output = {
                "tipo_analisis": analysis_type,
                "nombre_archivo": filename,
                "resultado": result
            }
            print(f"Resultado final: {final_output}")
            
            # Crear una respuesta JSON y añadir la cabecera para forzar la descarga
            # en el navegador del usuario como un archivo .json.
            response = jsonify(final_output)
            response.headers['Content-Disposition'] = f'attachment; filename=resultado_{os.path.splitext(filename)[0]}.json'
            return response
        
        #Codigo IA
        except genai.types.generation_types.BlockedPromptException as e:
            print(f"Análisis bloqueado por políticas de seguridad: {e}")
            return jsonify({"error": "El contenido fue bloqueado por las políticas de seguridad de la IA."}), 400
        
        except Exception as e:
            # Si ocurre cualquier otro error, lo imprimimos en la consola para poder depurarlo.
            import traceback
            print(f"Ocurrió un error inesperado: {traceback.format_exc()}")

            # Intentamos dar un mensaje de error más útil al usuario.
            # Si el error menciona la API Key, le damos una pista sobre cómo solucionarlo.
            error_str = str(e)
            if "API_KEY" in error_str or "permission" in error_str.lower():
                error_message = "Error de Autenticación con Google: La API Key fue rechazada. Por favor, verifica que la clave sea válida, que la 'Gemini API' esté habilitada en tu proyecto de Google Cloud y que la facturación esté activa."
            else:
                error_message = f"Error interno del servidor al comunicarse con la API de IA. Causa: {error_str}"

            return jsonify({"error": error_message}), 500

        finally:
            # Este es el paso de limpieza. No importa si el análisis fue exitoso o falló,
            # siempre borramos el archivo que el usuario subió para no llenar nuestro servidor.
            if os.path.exists(file_path):
                os.remove(file_path)

# Este es el punto de entrada estándar para una aplicación Python.
# Si ejecutamos `python app.py`, se iniciará el servidor de desarrollo de Flask.
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
