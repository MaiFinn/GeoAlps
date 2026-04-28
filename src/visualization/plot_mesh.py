import logging

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps
from matplotlib.colors import BoundaryNorm


logger = logging.getLogger(__name__)


def plot_terrain_mesh(
    x_grid,
    y_grid,
    z_grid,
    z_scale=1.0,
    title="Terrain Mesh",
    scale_reference="min",
    fix_z_axis=True,
    color_levels=8,
    colormap_name="terrain",
):
    """
    Plot a terrain mesh as a 3D surface.

    Parameters
    ----------
    x_grid : np.ndarray
        2D array containing x coordinates.
    y_grid : np.ndarray
        2D array containing y coordinates.
    z_grid : np.ndarray
        2D array containing original elevation values.
    z_scale : float
        Vertical scaling factor for elevation values.
    title : str
        Plot title.
    scale_reference : str
        Reference value used for vertical scaling.
        Supported values are "min", "mean", and "median".
    fix_z_axis : bool
        If True, keep the z-axis limits based on the original elevation range.
        If False, use the scaled z range.
    color_levels : int
        Number of discrete color levels used for the terrain surface.
    colormap_name : str
        Name of the matplotlib colormap.

    Raises
    ------
    ValueError
        If the input arrays are invalid or have incompatible shapes.
    """

    logger.info("Creating terrain mesh plot.")

    if x_grid is None or y_grid is None or z_grid is None:
        logger.error("One or more mesh arrays are None.")
        raise ValueError("x_grid, y_grid, and z_grid must not be None.")

    if x_grid.shape != y_grid.shape or x_grid.shape != z_grid.shape:
        logger.error(
            "Mesh array shapes do not match. x=%s, y=%s, z=%s",
            x_grid.shape,
            y_grid.shape,
            z_grid.shape,
        )
        raise ValueError(
            f"Mesh array shapes must match. "
            f"Got x={x_grid.shape}, y={y_grid.shape}, z={z_grid.shape}."
        )

    if z_scale <= 0:
        logger.error("Invalid z_scale: %s", z_scale)
        raise ValueError("z_scale must be greater than 0.")

    if color_levels < 2:
        logger.error("Invalid color_levels: %s", color_levels)
        raise ValueError("color_levels must be greater than or equal to 2.")

    valid_mask = np.isfinite(z_grid)
    valid_z_values = z_grid[valid_mask]

    if valid_z_values.size == 0:
        logger.error("No valid z values available for plotting.")
        raise ValueError("No valid z values available for plotting.")

    z_min = float(np.min(valid_z_values))
    z_max = float(np.max(valid_z_values))

    if z_min == z_max:
        logger.error("All valid z values are identical: %s", z_min)
        raise ValueError(f"All valid z values are identical: {z_min}.")

    if scale_reference == "min":
        z_reference = z_min
    elif scale_reference == "mean":
        z_reference = float(np.mean(valid_z_values))
    elif scale_reference == "median":
        z_reference = float(np.median(valid_z_values))
    else:
        logger.error("Invalid scale_reference: %s", scale_reference)
        raise ValueError("scale_reference must be one of: 'min', 'mean', or 'median'.")

    z_plot = z_reference + (z_grid - z_reference) * z_scale

    valid_z_plot_values = z_plot[np.isfinite(z_plot)]

    if valid_z_plot_values.size == 0:
        logger.error("No valid scaled z values available for plotting.")
        raise ValueError("No valid scaled z values available for plotting.")

    z_plot_min = float(np.min(valid_z_plot_values))
    z_plot_max = float(np.max(valid_z_plot_values))

    if z_plot_min == z_plot_max:
        logger.error("All valid scaled z values are identical: %s", z_plot_min)
        raise ValueError(f"All valid scaled z values are identical: {z_plot_min}.")

    valid_z_count = int(np.count_nonzero(valid_mask))
    total_z_count = int(z_grid.size)

    logger.info(
        "Plotting terrain mesh. Shape=%s, valid_z_values=%s, invalid_z_values=%s, "
        "z_scale=%s, scale_reference=%s, fix_z_axis=%s, color_levels=%s, "
        "original_z_min=%s, original_z_max=%s, scaled_z_min=%s, scaled_z_max=%s",
        z_grid.shape,
        valid_z_count,
        total_z_count - valid_z_count,
        z_scale,
        scale_reference,
        fix_z_axis,
        color_levels,
        z_min,
        z_max,
        z_plot_min,
        z_plot_max,
    )

    cmap = colormaps[colormap_name].resampled(color_levels)

    boundaries = np.linspace(z_plot_min, z_plot_max, color_levels + 1)
    norm = BoundaryNorm(boundaries, cmap.N)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    surface = ax.plot_surface(
        x_grid,
        y_grid,
        z_plot,
        linewidth=0,
        antialiased=True,
        cmap=cmap,
        norm=norm,
        rcount=z_plot.shape[0],
        ccount=z_plot.shape[1],
    )

    if fix_z_axis:
        ax.set_zlim(z_min, z_max)
    else:
        ax.set_zlim(z_plot_min, z_plot_max)

    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Elevation")

    colorbar = fig.colorbar(
        surface,
        ax=ax,
        shrink=0.6,
        aspect=12,
        boundaries=boundaries,
        ticks=boundaries,
    )

    if z_scale == 1.0:
        colorbar.set_label("Elevation")
    else:
        colorbar.set_label("Scaled elevation")

    logger.info("Displaying terrain mesh plot.")

    plt.tight_layout()
    plt.show()