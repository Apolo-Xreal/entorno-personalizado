"""
config.py — Punto de entrada que Qtile ejecuta al arrancar

Este archivo casi no tiene lógica propia: su trabajo es IMPORTAR el
contenido de los demás archivos (keys.py, layouts.py, groups.py,
bar.py) y juntarlos en las variables que Qtile espera encontrar.

Si algo falla al arrancar Qtile, revisa el log con:
    cat ~/.local/share/qtile/qtile.log
Y valida la sintaxis antes de reiniciar con:
    qtile check
"""

from libqtile.config import Screen, Click, Drag
from libqtile.lazy import lazy
import os
import subprocess
from keys import keys, mod
from layouts import layouts, floating_layout
from groups import groups, group_keys
from bar import main_bar, bar_position

# Juntamos los atajos "fijos" de keys.py con los generados
# automáticamente para los 9 escritorios en groups.py
keys = keys + group_keys

# Un único monitor. La posición de la barra (arriba/abajo) depende del
# estilo activo, calculado en bar.py como "top" o "bottom". El **
# desempaqueta ese texto como el nombre del argumento de Screen(), así
# que Screen(**{"top": main_bar}) es exactamente igual que escribir
# Screen(top=main_bar) a mano, pero permite que cambie dinámicamente.
screens = [
    Screen(**{bar_position: main_bar}),
]

# Permite mover/redimensionar ventanas flotantes arrastrando con el
# ratón mientras mantienes pulsado Super (mod).
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]
# --- Opciones generales de Qtile (valores por defecto sensatos) ---
dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True
wmname = "AYOS"

@hook.suscribe.strartup_once
def autostart():
    subprocess.Popen(["picom","--config", os.path.expanduser("~/.config/picom.conf")]
