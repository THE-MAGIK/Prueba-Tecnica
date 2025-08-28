# Analizador de Archivos con IA de Google Gemini

Este proyecto es una aplicación web construida con Flask que permite a los usuarios subir archivos de imagen o video para ser analizados por la IA de Google Gemini.

## Características

-   Sube archivos de imagen (PNG, JPG, JPEG, WEBP) y video (MP4, MOV, AVI, MKV).
-   Analiza el contenido de los archivos utilizando la API de Google Gemini.
-   Para imágenes, extrae información como contenido prohibido, información sensible, nombre y marca del producto, y descripción de uso.
-   Para videos, realiza una moderación de contenido para detectar material obsceno, racista, información personal o contenido sensible en general.
-   Devuelve los resultados del análisis en un archivo JSON.

## Capturas de Pantalla

**Página Principal:**
<img width="1149" height="546" alt="image" src="https://github.com/user-attachments/assets/87343116-8738-4639-9643-8727dabb066c" />

## **Ejemplo de imagen de producto "Fabuloso"**
## **Imagen:**
![images](https://github.com/user-attachments/assets/6fa02fac-c742-4bc4-b7fa-f94fae2a1d04)

## **Resultado json:**
<img width="562" height="234" alt="image" src="https://github.com/user-attachments/assets/a8778f65-d238-4fc4-b263-b4426763b85b" />

## **Ejemplo de imagen de productos prohibidos"**
## **Imagen:**
![Objetos-Prohibidos-en-el-Avion](https://github.com/user-attachments/assets/143b4cb9-f5cf-4035-8896-5eb8d5f11514)

## **Resultado json:**
<img width="1367" height="282" alt="image" src="https://github.com/user-attachments/assets/b72cd61a-7a88-433c-8582-92b53db862ce" />


## **Ejemplo de video donde hay racismo(Descargar si es necesario)**
## **video:**
**Link:** https://www.youtube.com/watch?v=AeT9jJdCDuc&ab_channel=MinisteriodeIgualdad

**Link de descarga:** https://www.ssyoutube.com/watch?v=AeT9jJdCDuc&ab_channel=MinisteriodeIgualdad

## **Resultado json:**
<img width="1017" height="467" alt="image" src="https://github.com/user-attachments/assets/d21d29c6-6d18-474b-a92c-d1fe864f8e9c" />


## **Ejemplo de video donde hay racismo, violencia (pelea), informacion personal y producto (fabuloso)**
## **video: Es un video personal el cual no mostrare**

## **Resultado json:**
<img width="1031" height="485" alt="image" src="https://github.com/user-attachments/assets/64787cb7-28ce-4475-ae21-8b096e5a0c71" />

## **Ejemplo de imagen descriminatoria**
## **Imagen:**
<img width="367" height="292" alt="image" src="https://github.com/user-attachments/assets/07db1c37-089c-43d6-b618-2da1b3a3d27c" />

## **Resultado json:**
<img width="1310" height="316" alt="image" src="https://github.com/user-attachments/assets/1aa24849-5936-498f-9d10-68df49739c97" />

## **Ejemplo de imagen con informacion personal**
## **Imagen:**
![WhatsApp Image 2025-08-28 at 5 18 17 PM](https://github.com/user-attachments/assets/948de255-3a7f-4c6a-866a-417e2f196ecd)

## **Resultado json:**
<img width="652" height="387" alt="image" src="https://github.com/user-attachments/assets/28c9016e-55a0-47f3-b482-0ac9e702f838" />






## Instalación

1.  Clona este repositorio:
    ```bash
    git clone https://github.com/THE-MAGIK/Prueba-Tecnica.git
    ```
2.  Navega al directorio del proyecto:
    ```bash
    cd Prueba-Tecnica
    ```
3.  Crea un entorno virtual:
    ```bash
    python -m venv venv
    ```
4.  Activa el entorno virtual:
    -   En Windows:
        ```bash
        venv\Scripts\activate
        ```
    -   En macOS y Linux:
        ```bash
        source venv/bin/activate
        ```
5.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
6.  Crea un archivo `.env` en la raíz del proyecto y añade tu API key de Google:
    ```
    GOOGLE_API_KEY="TU_API_KEY_DE_GOOGLE"
    ```

## Uso

1.  Ejecuta la aplicación:
    ```bash
    python app.py
    ```
2.  Abre tu navegador y ve a `http://127.0.0.1:5000`.
3.  Selecciona un archivo de imagen o video y haz clic en "Subir y Analizar".
4.  El resultado del análisis se descargará como un archivo JSON.
