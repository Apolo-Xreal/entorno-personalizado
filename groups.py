"""
groups.py — Escritorios / workspaces (1 al 9)

Un "grupo" en Qtile es lo que normalmente llamamos "escritorio virtual".
Aquí generamos 9 grupos (1-9) y, en un bucle, los atajos Super+1...Super+9
para cambiar de escritorio, y Super+Shift+1...9 para mover la ventana
activa a ese escritorio sin cambiarte tú.
"""

from libqtile.config import Group, Key
from libqtile.lazy import lazy

from keys import mod  # reutilizamos el mismo modificador que en keys.py

# Crea los 9 grupos, nombrados simplemente "1" a "9"
groups = [Group(str(i)) for i in range(1, 10)]

# Genera automáticamente los atajos de teclado para cada grupo, en vez
# de escribir 9 Key() casi idénticas a mano.
group_keys = []
for grp in groups:
    group_keys.extend([
        Key([mod], grp.name,
            lazy.group[grp.name].toscreen(),
            desc=f"Cambiar al escritorio {grp.name}"),

        Key([mod, "shift"], grp.name,
            lazy.window.togroup(grp.name, switch_group=False),
            desc=f"Mover la ventana activa al escritorio {grp.name}"),
    ])
