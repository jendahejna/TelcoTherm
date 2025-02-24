import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from config import COLORS, TEMP_OFFSET
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
from config import COLORBAR_SETTINGS
import logging

n_levels = COLORBAR_SETTINGS["n_levels"]
backend_logger = logging.getLogger('backend_logger')

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


def map_plotting(grid_x, grid_y, grid_z, czech_rep, image_name, show_boundary=False):
    backend_logger.info("map_plotting function started with image name: %s", image_name)
    try:
        # Create custom colormap
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "custom_colormap",
            COLORBAR_SETTINGS["colormap"],
            N=n_levels,
        )


        # Calculate median and set color limits
        median_value = np.median(grid_z[~np.isnan(grid_z)]) - 2
        vmin = int(median_value) - 7
        vmax = int(median_value) + 7
        backend_logger.debug("Calculated median value: %f, vmin: %d, vmax: %d", median_value, vmin, vmax)

        # Create figure and axis for plotting
        fig, ax = plt.subplots(figsize=(8, 4), frameon=False)


        # Create the pcolormesh plot
        c = ax.pcolormesh(
            grid_x, grid_y, grid_z,
            cmap=cmap,
            shading="auto",
            edgecolor="none",
            vmin=vmin,
            vmax=vmax
        )

        # Plot boundaries if requested
        if show_boundary:
            czech_rep.boundary.plot(ax=ax, linewidth=1, color="black")

        # Remove axes for a cleaner look
        ax.set_axis_off()

        # Create the directory if it doesn't exist and build the save path
        save_dir = "images"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{image_name}")

        # Save the figure to file
        plt.savefig(
            save_path,
            format="png",
            dpi=150,
            transparent=True,
            bbox_inches="tight",
            pad_inches=0,
        )
        plt.close(fig)

        backend_logger.info("Plot saved successfully at %s", save_path)

    except Exception as e:
        backend_logger.exception("Exception in map_plotting function: %s", e)
        raise

