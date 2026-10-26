import os
from libqtile import bar, widget

# Ruta del archivo que guardará el estado
STATE_FILE = os.path.expanduser("~/.config/qtile/.bar_style")

def get_current_style():
    """Lee el archivo de estado. Si no existe, por defecto es macOS."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            style = f.read().strip()
            if style in ["macos", "windows"]:
                return style
    return "macos"

def toggle_style_state():
    """Cambia el estado en el archivo para la próxima recarga."""
    current = get_current_style()
    new_style = "windows" if current == "macos" else "macos"
    with open(STATE_FILE, "w") as f:
        f.write(new_style)

def toggle_bar_style(qtile):
    """
    Esta es la función que faltaba conectar: cambia el estado guardado
    y le pide a Qtile que se recargue. Al recargarse, config.py vuelve
    a ejecutar este archivo desde cero, get_current_style() lee el
    nuevo valor, y por eso la barra "cambia" de estilo.

    Se llama desde un atajo de teclado en keys.py mediante
    lazy.function(toggle_bar_style).
    """
    toggle_style_state()
    qtile.reload_config()

# --- DISEÑO: ESTILO MACOS ---
widgets_macos = [
    widget.WindowName(padding=10),
    widget.Spacer(),
    widget.GroupBox(active="#ffffff", inactive="#8e8e93", highlight_method="text", padding=6),
    widget.Sep(padding=6),
    widget.Systray(),
    widget.Sep(padding=6),
    widget.Clock(format="%a %d %b  %H:%M"),
]

bar_macos = bar.Bar(
    widgets_macos,
    26,
    background="#f5f5f7cc",
    opacity=0.95,
    margin=[4, 6, 0, 6] # Un pequeño margen superior flotante estilo macOS
)

# --- DISEÑO: ESTILO WINDOWS 10 ---
widgets_windows = [
    # Grupos a la izquierda con estilo de bloque/línea simulando la taskbar
    widget.GroupBox(
        active="#ffffff",
        inactive="#555555",
        highlight_method="line",
        highlight_color=["#1f1f1f", "#0078d7"], # Azul clásico de Windows 10
        this_current_screen_border="#0078d7",
        padding=8,
        margin_x=0,
    ),
    widget.Sep(padding=10),
    widget.WindowName(padding=10),
    widget.Spacer(),
    widget.Systray(),
    widget.Sep(padding=10),
    # Reloj completo a la derecha con fecha y hora juntas
    widget.Clock(format="%H:%M\n%d/%m/%Y", padding=10), 
]

bar_windows = bar.Bar(
    widgets_windows,
    40, # Las barras de Windows 10 son notablemente más gruesas
    background="#101010", # Fondo oscuro sólido
    opacity=1.0
)

# --- LÓGICA DE SELECCIÓN ---
style = get_current_style()

if style == "windows":
    main_bar = bar_windows
    bar_position = "bottom" # Windows: abajo
else:
    main_bar = bar_macos
    bar_position = "top"    # macOS: arriba