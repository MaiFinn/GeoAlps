import logging

import numpy as np
import pyvista as pv


logger = logging.getLogger(__name__)


def plot_terrain_3d(
    x_grid,
    y_grid,
    z_grid,
    z_scale=1.0,
    title="3D Terrain Render",
    colormap_name="terrain",
    show_edges=False,
    show_grid=True,
):
    """
    Render a cropped terrain mesh as an interactive 3D surface using PyVista.

    The function converts geographic x/y coordinates to approximate local
    metric coordinates so that x, y, and z are visually comparable.

    Parameters
    ----------
    x_grid : np.ndarray
        2D array containing x coordinates, usually longitude values.
    y_grid : np.ndarray
        2D array containing y coordinates, usually latitude values.
    z_grid : np.ndarray
        2D array containing elevation values in meters.
    z_scale : float
        Vertical exaggeration factor for the terrain.
    title : str
        Window title.
    colormap_name : str
        Name of the colormap used for elevation coloring.
    show_edges : bool
        If True, show mesh edges.
    show_grid : bool
        If True, show a coordinate grid in the PyVista scene.

    Raises
    ------
    ValueError
        If the input arrays are invalid or incompatible.
    """

    logger.info("Starting 3D terrain rendering.")

    if x_grid is None or y_grid is None or z_grid is None:
        logger.error("One or more input grids are None.")
        raise ValueError("x_grid, y_grid, and z_grid must not be None.")

    if x_grid.shape != y_grid.shape or x_grid.shape != z_grid.shape:
        logger.error(
            "Grid shapes do not match. x=%s, y=%s, z=%s",
            x_grid.shape,
            y_grid.shape,
            z_grid.shape,
        )
        raise ValueError(
            f"Grid shapes must match. "
            f"Got x={x_grid.shape}, y={y_grid.shape}, z={z_grid.shape}."
        )

    if z_scale <= 0:
        logger.error("Invalid z_scale: %s", z_scale)
        raise ValueError("z_scale must be greater than 0.")

    valid_z_mask = np.isfinite(z_grid)
    valid_z_values = z_grid[valid_z_mask]

    if valid_z_values.size == 0:
        logger.error("No valid elevation values available for rendering.")
        raise ValueError("No valid elevation values available for rendering.")

    z_min = float(np.min(valid_z_values))
    z_max = float(np.max(valid_z_values))

    if z_min == z_max:
        logger.error("All valid elevation values are identical: %s", z_min)
        raise ValueError(f"All valid elevation values are identical: {z_min}.")

    logger.info(
        "Elevation range before scaling: min=%s, max=%s",
        z_min,
        z_max,
    )

    x_local, y_local = _convert_lon_lat_to_local_meters(x_grid, y_grid)

    z_local = _scale_elevation(
        z_grid=z_grid,
        z_scale=z_scale,
        z_reference=z_min,
    )

    # PyVista cannot reliably render NaN coordinates.
    # Invalid elevation cells are flattened to the minimum elevation.
    z_local_clean = np.where(np.isfinite(z_local), z_local, z_min)

    logger.info(
        "Local coordinate ranges | x: %.2f to %.2f m, y: %.2f to %.2f m, z: %.2f to %.2f m",
        float(np.nanmin(x_local)),
        float(np.nanmax(x_local)),
        float(np.nanmin(y_local)),
        float(np.nanmax(y_local)),
        float(np.nanmin(z_local_clean)),
        float(np.nanmax(z_local_clean)),
    )

    terrain_grid = pv.StructuredGrid(
        x_local,
        y_local,
        z_local_clean,
    )

    # Use original elevation values for coloring.
    elevation_values = z_grid.astype("float64", copy=False).ravel(order="F")
    terrain_grid["Elevation"] = elevation_values

    plotter = pv.Plotter(window_size=(1400, 900))
    plotter.add_text(title, font_size=12)

    plotter.add_mesh(
        terrain_grid,
        scalars="Elevation",
        cmap=colormap_name,
        show_edges=show_edges,
        smooth_shading=True,
        nan_color="gray",
        scalar_bar_args={
            "title": "Elevation [m]",
            "vertical": True,
        },
    )

    if show_grid:
        plotter.show_grid(
            xlabel="X [m]",
            ylabel="Y [m]",
            zlabel="Elevation [m]",
        )
    else:
        plotter.show_axes()

    _set_terrain_camera(plotter, x_local, y_local, z_local_clean)

    logger.info("Displaying 3D terrain render.")

    plotter.show(title=title)


def _convert_lon_lat_to_local_meters(x_grid, y_grid):
    """
    Convert longitude/latitude coordinates to approximate local metric coordinates.

    Parameters
    ----------
    x_grid : np.ndarray
        Longitude grid.
    y_grid : np.ndarray
        Latitude grid.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Local x and y coordinates in meters.
    """

    mean_latitude = float(np.nanmean(y_grid))

    meters_per_degree_lat = 111_320.0
    meters_per_degree_lon = 111_320.0 * np.cos(np.deg2rad(mean_latitude))

    x_local = (x_grid - np.nanmin(x_grid)) * meters_per_degree_lon
    y_local = (y_grid - np.nanmin(y_grid)) * meters_per_degree_lat

    return x_local, y_local


def _scale_elevation(z_grid, z_scale, z_reference):
    """
    Scale elevation values around a reference elevation.

    Parameters
    ----------
    z_grid : np.ndarray
        Original elevation grid.
    z_scale : float
        Vertical exaggeration factor.
    z_reference : float
        Reference elevation used as scaling anchor.

    Returns
    -------
    np.ndarray
        Scaled elevation grid.
    """

    return z_reference + (z_grid - z_reference) * z_scale


def _set_terrain_camera(plotter, x_local, y_local, z_local):
    """
    Set a useful initial camera position for terrain visualization.

    Parameters
    ----------
    plotter : pyvista.Plotter
        Active PyVista plotter.
    x_local : np.ndarray
        Local x coordinates in meters.
    y_local : np.ndarray
        Local y coordinates in meters.
    z_local : np.ndarray
        Local z coordinates in meters.
    """

    x_min = float(np.nanmin(x_local))
    x_max = float(np.nanmax(x_local))
    y_min = float(np.nanmin(y_local))
    y_max = float(np.nanmax(y_local))
    z_min = float(np.nanmin(z_local))
    z_max = float(np.nanmax(z_local))

    x_center = 0.5 * (x_min + x_max)
    y_center = 0.5 * (y_min + y_max)
    z_center = 0.5 * (z_min + z_max)

    x_range = x_max - x_min
    y_range = y_max - y_min
    z_range = max(z_max - z_min, 1.0)

    max_range = max(x_range, y_range, z_range)

    camera_position = (
        x_center + 0.9 * max_range,
        y_center - 1.1 * max_range,
        z_center + 0.7 * max_range,
    )

    focal_point = (
        x_center,
        y_center,
        z_center,
    )

    view_up = (0, 0, 1)

    plotter.camera_position = [
        camera_position,
        focal_point,
        view_up,
    ]