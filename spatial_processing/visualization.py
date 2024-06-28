import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from config import COLORS, TEMP_OFFSET
from mpl_toolkits.axes_grid1 import make_axes_locatable


def get_heatmap(
    grid_x,
    grid_y,
    grid_z,
    czech_rep,
    save_path,
    show_colorbar=True,
    show_boundaries=False,
):
    min_temp = np.nanmin(grid_z)
    max_temp = np.nanmax(grid_z)
    n_levels = 30
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "custom_colormap",
        [
            (0, "navy"),  # cold temperatures
            (0.2, "blue"),
            (0.4, "green"),
            (0.6, "yellow"),
            (0.8, "orange"),
            (1, "red"),  # warm temperatures
        ],
        N=n_levels,
    )
    fig, ax = plt.subplots(figsize=(8, 4), frameon=False)

    c = ax.pcolormesh(
        grid_x,
        grid_y,
        grid_z,
        cmap=cmap,
        shading="auto",
        edgecolor="none",
        vmin=min_temp,
        vmax=max_temp,
    )
    if show_boundaries:
        czech_rep.boundary.plot(ax=ax, linewidth=0.5, color="black")

    for spine in ax.spines.values():
        spine.set_visible(False)

    if show_colorbar:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = plt.colorbar(c, cax=cax)
        cbar.ax.tick_params(labelsize=10)

    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_xlim([grid_x.min(), grid_x.max()])
    ax.set_ylim([grid_y.min(), grid_y.max()])

    plt.savefig(
        save_path,
        format="png",
        dpi=150,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0,
    )
    plt.show()
    plt.close()
