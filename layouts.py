"""
layouts.py — Cómo se organizan las ventanas

Un "layout" en Qtile es un algoritmo que decide dónde y con qué tamaño
se coloca cada ventana. Puedes tener varios layouts definidos y cambiar
entre ellos en caliente (con un atajo, que añadiremos si lo quieres).
"""

from libqtile import layout

# Colores usados para el borde de las ventanas según si están enfocadas
# o no. Cámbialos cuando definamos la paleta de colores del proyecto.
BORDE_ACTIVO = "#89b4fa"
BORDE_INACTIVO = "#313244"

layouts = [
    # Layout principal: tiling en columnas. Las ventanas se reparten
    # en columnas verticales, similar a como pediste ("prácticamente
    # igual" a tiling normal).
    layout.Columns(
        border_focus=BORDE_ACTIVO,
        border_normal=BORDE_INACTIVO,
        border_width=2,
        margin=6,          # espacio entre ventanas
    ),

    # Layout secundario: una ventana a pantalla completa (sin dividir).
    # Útil como alternativa rápida al tiling, se cambia entre layouts
    # con un atajo de teclado (lo añadimos si lo quieres en v1.1).
    layout.Max(),
]

# Layout especial para ventanas flotantes (las que "flotan" en vez de
# encajar en la rejilla de tiling). Aquí es donde en el futuro (v2)
# añadiremos bordes redondeados, pero eso requiere un compositor externo
# (picom) que Qtile por sí solo no puede hacer — ver notas del proyecto.
floating_layout = layout.Floating(
    border_focus=BORDE_ACTIVO,
    border_normal=BORDE_INACTIVO,
    border_width=2,
    float_rules=[
        # Reglas por defecto de Qtile: ventanas como diálogos de
        # confirmación, popups, etc. se abren flotando automáticamente
        # en vez de intentar encajarlas en el tiling.
        *layout.Floating.default_float_rules,
    ],
)
