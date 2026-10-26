"""
assistant.py — Asistente de IA integrado (v2: código, archivos, fondos)

Protocolo de respuesta del modelo: le pedimos que SIEMPRE responda con
un JSON de una de estas formas. Esto reemplaza el "ACCION:" de texto
plano de la v1, porque ahora necesitamos pasar datos (rutas, contenido
de código), no solo un nombre fijo.

  {"tipo": "accion_fija", "nombre": "<una de ACTIONS>"}
  {"tipo": "abrir_archivo", "ruta": "<ruta relativa a tu carpeta de usuario>"}
  {"tipo": "cambiar_fondo", "ruta": "<ruta de una imagen>"}
  {"tipo": "escribir_codigo", "archivo": "<nombre_archivo.py>", "contenido": "<código>"}
  {"tipo": "respuesta", "texto": "<respuesta normal en texto>"}

IMPORTANTE sobre seguridad:
  - El código que el asistente escribe SE GUARDA pero NUNCA SE EJECUTA
    automáticamente. Tienes que abrirlo y correrlo tú a mano.
  - Los archivos que puede escribir/abrir están limitados a carpetas
    concretas (ver config_paths.py), nunca a rutas arbitrarias del sistema.
"""

import subprocess
import json
import os

import requests

from actions import ACTIONS
from config_paths import HOME, CODE_SANDBOX, WALLPAPER_DIR

# Modelo orientado a código, versión ligera: rápido y con poco consumo de RAM, a cambio de peor calidad en peticiones de código complejas o ambiguas. Si más adelante tu PC lo aguanta y quieres mejor calidad, cambia esto a "qwen2.5-coder:7b" (necesita bastante más RAM).

MODEL = "qwen2.5-coder:1.5b"
OLLAMA_URL = "http://localhost:11434/api/generate"


def get_user_input():
    """Abre Rofi en modo caja de texto y devuelve lo que escribiste."""
    try:
        result = subprocess.run(
            ["rofi", "-dmenu", "-p", "Asistente IA"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        notify("Rofi no esta instalado (sudo apt install rofi).")
        return ""
    return result.stdout.strip()


def build_system_prompt():
    nombres_acciones = ", ".join(ACTIONS.keys())
    return f"""Eres un asistente integrado en un sistema operativo Linux.
Debes responder SIEMPRE con un unico objeto JSON, sin texto adicional
ni explicaciones fuera del JSON, usando uno de estos formatos exactos:

1. Accion fija del sistema (valores posibles de "nombre": {nombres_acciones}):
   {{"tipo": "accion_fija", "nombre": "<nombre_exacto>"}}

2. Abrir un archivo existente del usuario:
   {{"tipo": "abrir_archivo", "ruta": "<ruta relativa a la carpeta personal>"}}

3. Cambiar el fondo de pantalla (la imagen debe existir):
   {{"tipo": "cambiar_fondo", "ruta": "<ruta de la imagen>"}}

4. Escribir codigo que el usuario pidió:
   {{"tipo": "escribir_codigo", "archivo": "<nombre_archivo_con_extension>", "contenido": "<codigo_completo>"}}

5. Cualquier otra pregunta o peticion que no encaje arriba:
   {{"tipo": "respuesta", "texto": "<tu respuesta breve>"}}

Responde UNICAMENTE con el JSON, nada mas."""


def ask_ollama(user_text):
    payload = {
        "model": MODEL,
        "system": build_system_prompt(),
        "prompt": user_text,
        "stream": False,
        "format": "json",  # Ollama fuerza una salida JSON válida
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["response"].strip()


def notify(text):
    """
    Muestra una notificación. Si 'notify-send' no está instalado (o
    falla por cualquier motivo), lo imprimimos por consola en vez de
    dejar que el programa reviente sin avisar. Como esto se lanza desde
    un atajo de teclado, sin este 'try' nunca te enterarías del fallo.
    """
    try:
        subprocess.run(["notify-send", "Asistente IA", text], timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"[Asistente IA] (no se pudo notificar: {e}) {text}")


def safe_path_in(base_dir, relative_path):
    """
    Resuelve relative_path dentro de base_dir y comprueba que el
    resultado sigue estando DENTRO de base_dir. Esto es lo que evita
    que algo como "../../etc/passwd" se escape de la carpeta permitida.
    Devuelve la ruta segura, o None si el intento se sale de la carpeta.
    """
    candidate = os.path.realpath(os.path.join(base_dir, relative_path))
    base = os.path.realpath(base_dir)
    if candidate == base or candidate.startswith(base + os.sep):
        return candidate
    return None


def handle_accion_fija(data):
    nombre = data.get("nombre", "")
    command = ACTIONS.get(nombre)
    if command:
        subprocess.Popen(command, shell=True)
        notify(f"Ejecutando: {nombre}")
    else:
        notify(f"Accion desconocida sugerida: {nombre}")


def handle_abrir_archivo(data):
    ruta_segura = safe_path_in(HOME, data.get("ruta", ""))
    if ruta_segura and os.path.exists(ruta_segura):
        subprocess.Popen(["xdg-open", ruta_segura])
        notify(f"Abriendo: {ruta_segura}")
    else:
        notify("No encuentro ese archivo o esta fuera de tu carpeta personal.")


def handle_cambiar_fondo(data):
    ruta_segura = safe_path_in(HOME, data.get("ruta", ""))
    if ruta_segura and os.path.exists(ruta_segura):
        # Requiere "feh" instalado: sudo apt install feh
        subprocess.Popen(["feh", "--bg-fill", ruta_segura])
        notify("Fondo de pantalla cambiado.")
    else:
        notify("No encuentro esa imagen o esta fuera de tu carpeta personal.")


def handle_escribir_codigo(data):
    # Solo el nombre del archivo, nunca una ruta con carpetas: asi nos
    # aseguramos de que SIEMPRE se guarda dentro de CODE_SANDBOX, sin
    # importar lo que el modelo intente meter en "archivo".
    nombre_archivo = os.path.basename(data.get("archivo", "codigo_sin_nombre.txt"))
    contenido = data.get("contenido", "")

    ruta_final = os.path.join(CODE_SANDBOX, nombre_archivo)
    with open(ruta_final, "w") as f:
        f.write(contenido)

    # Se guarda, pero NUNCA se ejecuta automaticamente.
    subprocess.Popen(["xdg-open", ruta_final])
    notify(f"Codigo guardado en: {ruta_final}\n(revisalo antes de ejecutarlo)")


def handle_respuesta(data):
    notify(data.get("texto", "(respuesta vacia)"))


HANDLERS = {
    "accion_fija": handle_accion_fija,
    "abrir_archivo": handle_abrir_archivo,
    "cambiar_fondo": handle_cambiar_fondo,
    "escribir_codigo": handle_escribir_codigo,
    "respuesta": handle_respuesta,
}


def main():
    user_text = get_user_input()
    if not user_text:
        return  # Esc en Rofi, no hacemos nada

    try:
        raw_reply = ask_ollama(user_text)
    except requests.exceptions.ConnectionError:
        notify("No puedo conectar con Ollama. ¿Esta corriendo? (ollama serve)")
        return
    except requests.exceptions.Timeout:
        notify("Ollama ha tardado demasiado en responder (timeout de 120s).")
        return
    except requests.exceptions.HTTPError as e:
        notify(f"Ollama devolvio un error: {e}")
        return
    except requests.exceptions.RequestException as e:
        # Red de seguridad para cualquier otro fallo de 'requests' que
        # no hayamos previsto explicitamente arriba.
        notify(f"Fallo al hablar con Ollama: {e}")
        return

    # Ollama fuerza JSON con format="json", pero por si acaso el modelo
    # metiera la respuesta envuelta en ```json ... ```, lo limpiamos
    # antes de parsear en vez de fallar directamente.
    raw_reply_limpio = raw_reply.strip()
    if raw_reply_limpio.startswith("```json"):
        raw_reply_limpio = raw_reply_limpio[len("```json"):]
    elif raw_reply_limpio.startswith("```"):
        raw_reply_limpio = raw_reply_limpio[len("```"):]
    if raw_reply_limpio.endswith("```"):
        raw_reply_limpio = raw_reply_limpio[:-len("```")]
    raw_reply_limpio = raw_reply_limpio.strip()

    try:
        data = json.loads(raw_reply_limpio)
    except json.JSONDecodeError:
        # El modelo no devolvio JSON valido: se lo mostramos tal cual
        # en vez de fallar en silencio, para que veas que paso.
        notify(f"Respuesta no reconocida: {raw_reply[:200]}")
        return

    tipo = data.get("tipo", "")
    handler = HANDLERS.get(tipo)
    if handler:
        try:
            handler(data)
        except Exception as e:
            # Si un handler falla (p. ej. permisos al escribir un
            # archivo, feh no instalado, etc.) te avisamos en vez de
            # que el proceso muera sin dejar rastro.
            notify(f"Error al ejecutar '{tipo}': {e}")
    else:
        notify(f"Tipo de respuesta desconocido: {tipo}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Red de seguridad final: como este script se lanza desde un
        # atajo de teclado sin terminal visible, sin esto un error no
        # previsto se perdería para siempre. Al menos así lo ves en
        # una notificacion.
        notify(f"Error inesperado en el asistente: {e}")
