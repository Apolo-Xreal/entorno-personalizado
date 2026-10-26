"""
keys.py — Atajos de teclado

Aquí se definen todas las combinaciones de teclas. Cada Key() tiene:
  1. Lista de modificadores (ej. [mod] = Super, ["mod1"] = Alt)
  2. La tecla en sí (ej. "t")
  3. La acción a ejecutar (lazy.spawn(...) para abrir programas,
     lazy.window.xxx() para actuar sobre la ventana activa)
  4. desc = descripción (no afecta al funcionamiento, es documentación)
"""

from libqtile.config import Key
from libqtile.lazy import lazy

# Importamos la función de bar.py que faltaba conectar a un atajo.
# Esto es lo que realmente activa el cambio de estilo macOS <-> Windows.
from bar import toggle_bar_style

# Tecla Super/Windows como modificador principal.
# NOTA: en tu lista original pusiste "Supr", que en teclados en español
# suele ser la tecla Delete. La convención en Linux para esto es la tecla
# Super (Windows), así que la uso aquí. Si de verdad querías Delete,
# cambia "mod4" por "Delete" — pero ojo, usar Delete como modificador
# constante puede dar problemas porque algunas apps ya usan esa tecla sola.
mod = "mod4"

terminal = "alacritty"
file_manager = "pcmanfm"  # cámbialo si usas otro (nautilus, thunar, etc.)

keys = [
    # ---------- Aplicaciones ----------
    Key([mod], "t", lazy.spawn(terminal),
        desc="Abrir terminal"),

    Key([mod], "a", lazy.spawn(file_manager),
        desc="Abrir gestor de archivos"),

    # La "rejilla de aplicaciones" no es nativa de Qtile, pero Rofi ya
    # trae un modo de cuadrícula (drun) que cumple la misma función.
    Key([], "Menu", lazy.spawn(
        "rofi -show drun -drun-display-format '{icon} {name}'"
    ), desc="Abrir rejilla de aplicaciones (Rofi)"),

    # ---------- Ventanas ----------
    Key(["mod1"], "Tab", lazy.layout.next(),
        desc="Cambiar a la siguiente ventana abierta"),

    Key(["mod1", mod], "Tab", lazy.screen.next_group(),
        desc="Cambiar al siguiente escritorio"),

    # OJO: "cerrar TODAS las ventanas abiertas" de golpe es arriesgado
    # (pierdes trabajo sin guardar en cualquier app). De momento este
    # atajo cierra solo la ventana activa. Si de verdad quieres el
    # comportamiento de cerrar todas a la vez, lo hacemos con una función
    # aparte y avisando antes — dilo y lo añadimos.
    Key(["mod1"], "Escape", lazy.window.kill(),
        desc="Cerrar la ventana activa"),

    # Maximizar/restaurar por atajo (no hay botón clicable en v1,
    # ver notas del proyecto sobre decoraciones de ventana).
    Key([mod], "m", lazy.window.toggle_maximize(),
        desc="Maximizar o restaurar la ventana activa"),

    Key([mod], "space", lazy.window.toggle_floating(),
        desc="Alternar ventana flotante / en tiling"),

    # ---------- Escritorios (grupos 1-9) ----------
    # Los atajos Super+1 a Super+9 se generan automáticamente en
    # groups.py a partir de la lista de grupos, para no repetir código
    # 9 veces aquí.

    # ---------- Capturas y utilidades ----------
    Key(["control", "shift"], "F6", lazy.spawn("flameshot gui"),
        desc="Captura de pantalla (selección interactiva)"),

    # Placeholder: la lógica real del asistente de IA es la Fase 5 del
    # proyecto. De momento este atajo solo confirma que la combinación
    # funciona.
    Key(["control", mod], "space",
        lazy.spawn("notify-send 'Asistente IA' 'Pendiente de implementar (Fase 5)'"),
        desc="Abrir asistente de IA (placeholder)"),

    # ---------- Control de Qtile ----------
    Key([mod, "control"], "r", lazy.reload_config(),
        desc="Recargar la configuración sin cerrar sesión"),

    Key([mod, "control"], "q", lazy.shutdown(),
        desc="Cerrar Qtile por completo"),

    # Este era el atajo que faltaba: alterna el estilo de la barra
    # (macOS <-> Windows 10). Usa lazy.function() en vez de lazy.spawn()
    # porque toggle_bar_style necesita acceso al objeto "qtile" interno
    # para poder recargar la configuración; no es un programa externo.
    Key([mod, "shift"], "b", lazy.function(toggle_bar_style),
        desc="Alternar estilo de barra: macOS <-> Windows 10"),
]
