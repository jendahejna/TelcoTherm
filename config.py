GRID_RESOLUTION_X = complex("1280j").imag  # X Rozlišení gridu
GRID_RESOLUTION_Y = complex("720j").imag  # Y Rozlišení gridu
TEMP_OFFSET = 5  # Offset pro teplotní škálu
COLORS = [  # Stará barevná škála pro vizualizaci barev v heatmapě
    "#490362",
    "#4e00a6",
    "#3600d0",
    "#0032f7",
    "#0467ff",
    "#04a3ff",
    "#00a2ff",
    "#04d27f",
    "#1bec38",
    "#63ff00",
    "#acfb02",
    "#fde516",
    "#f7c41b",
    "#f4fb0d",
    "#fc871d",
    "#db4f08",
    "#f73100",
    "#a00000",
    "#9f0000",
    "#5b0100",
]

COLORBAR_SETTINGS = {#Nové nastavení barevné škály
    "n_levels": 15,
    "colormap": [
        (0, "#4E00A6"),  # darkmagenta
        (1 / 14, "#3600D0"),  # mediumblue
        (2 / 14, "#1107F4"),  # blue
        (3 / 14, "#0032F7"),  # royalblue
        (4 / 14, "#0467FF"),  # deepskyblue
        (5 / 14, "#04A3FF"),  # lightskyblue
        (6 / 14, "#04D27F"),  # springgreen
        (7 / 14, "#1BEC38"),  # limegreen
        (8 / 14, "#63FF00"),  # lime
        (9 / 14, "#F4FB0D"),  # goldenyellow
        (10 / 14, "#FBE316"),  # darkgoldenrod
        (11 / 14, "#F7C41B"),  # orange
        (12 / 14, "#FC871D"),  # darkorange
        (13 / 14, "#DB4F08"),  # tomato
        (1, "#A00000"),  # maroon
    ],
}

