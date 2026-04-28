import logging
from pathlib import Path

import numpy as np
import pyvista as pv


logger = logging.getLogger(__name__)


def export_terrain_to_stl(
    x_grid,
    y_grid,
    z_grid,
    output_path,
    target_size_mm=150.0,
    base_thickness_mm=3.0,
    z_exaggeration=2.0,
    input_coordinates="degrees",
):
    """
    Export a terrain mesh as a watertight STL file for 3D printing.

    Parameters
    ----------
    x_grid : np.ndarray
        2D array containing x coordinates. Usually longitude or projected x values.
    y_grid : np.ndarray
        2D array containing y coordinates. Usually latitude or projected y values.
    z_grid : np.ndarray
        2D array containing elevation values in meters.
    output_path : str | Path
        Output path for the STL file.
    target_size_mm : float
        Maximum horizontal model size in millimeters.
    base_thickness_mm : float
        Thickness of the flat base below the terrain.
    z_exaggeration : float
        Vertical exaggeration factor for the terrain relief.
    input_coordinates : str
        Coordinate type of x_grid and y_grid.
        Supported values are "degrees" and "meters".

    Returns
    -------
    Path
        Path to the exported STL file.

    Raises
    ------
    ValueError
        If the input arrays are invalid.
    """

    logger.info("Starting STL terrain export.")

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

    if target_size_mm <= 0:
        raise ValueError("target_size_mm must be greater than 0.")

    if base_thickness_mm <= 0:
        raise ValueError("base_thickness_mm must be greater than 0.")

    if z_exaggeration <= 0:
        raise ValueError("z_exaggeration must be greater than 0.")

    rows, cols = z_grid.shape

    if rows < 2 or cols < 2:
        raise ValueError("Terrain grid must have at least 2 rows and 2 columns.")

    valid_z_mask = np.isfinite(z_grid)
    valid_z_values = z_grid[valid_z_mask]

    if valid_z_values.size == 0:
        raise ValueError("No valid elevation values available for STL export.")

    z_min = float(np.min(valid_z_values))
    z_max = float(np.max(valid_z_values))

    logger.info("Original elevation range: min=%s, max=%s", z_min, z_max)

    z_clean = np.where(np.isfinite(z_grid), z_grid, z_min)

    if input_coordinates == "degrees":
        x_local_m, y_local_m = _convert_lon_lat_to_local_meters(x_grid, y_grid)
    elif input_coordinates == "meters":
        x_local_m = x_grid - np.nanmin(x_grid)
        y_local_m = y_grid - np.nanmin(y_grid)
    else:
        raise ValueError("input_coordinates must be either 'degrees' or 'meters'.")

    x_range_m = float(np.nanmax(x_local_m) - np.nanmin(x_local_m))
    y_range_m = float(np.nanmax(y_local_m) - np.nanmin(y_local_m))

    max_range_m = max(x_range_m, y_range_m)

    if max_range_m <= 0:
        raise ValueError("Invalid x/y coordinate range.")

    xy_scale = target_size_mm / max_range_m

    x_mm = x_local_m * xy_scale
    y_mm = y_local_m * xy_scale

    z_mm = base_thickness_mm + (z_clean - z_min) * xy_scale * z_exaggeration

    bottom_z_mm = 0.0

    model_width = float(np.nanmax(x_mm) - np.nanmin(x_mm))
    model_depth = float(np.nanmax(y_mm) - np.nanmin(y_mm))
    model_height = float(np.nanmax(z_mm) - bottom_z_mm)

    logger.info(
        "STL model dimensions approx. width=%.2f mm, depth=%.2f mm, height=%.2f mm",
        model_width,
        model_depth,
        model_height,
    )

    vertices, faces = _build_watertight_terrain_mesh(
        x_mm=x_mm,
        y_mm=y_mm,
        z_mm=z_mm,
        bottom_z_mm=bottom_z_mm,
    )

    mesh = pv.PolyData(vertices, faces)

    if not mesh.is_all_triangles:
        logger.warning("Generated STL mesh is not fully triangulated. Triangulating now.")
        mesh = mesh.triangulate()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Saving STL file to: %s", output_path)

    mesh.save(output_path)

    logger.info("STL export finished successfully.")

    return output_path


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

    x_local_m = (x_grid - np.nanmin(x_grid)) * meters_per_degree_lon
    y_local_m = (y_grid - np.nanmin(y_grid)) * meters_per_degree_lat

    return x_local_m, y_local_m


def _build_watertight_terrain_mesh(x_mm, y_mm, z_mm, bottom_z_mm):
    """
    Build a watertight triangular terrain mesh with top, sides, and bottom.

    Parameters
    ----------
    x_mm : np.ndarray
        X coordinates in millimeters.
    y_mm : np.ndarray
        Y coordinates in millimeters.
    z_mm : np.ndarray
        Top terrain elevation in millimeters.
    bottom_z_mm : float
        Bottom plane height in millimeters.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Vertices and PyVista face array.
    """

    rows, cols = z_mm.shape

    top_vertices = np.column_stack(
        [
            x_mm.ravel(),
            y_mm.ravel(),
            z_mm.ravel(),
        ]
    )

    bottom_vertices = np.column_stack(
        [
            x_mm.ravel(),
            y_mm.ravel(),
            np.full(rows * cols, bottom_z_mm),
        ]
    )

    vertices = np.vstack([top_vertices, bottom_vertices])

    bottom_offset = rows * cols

    faces = []

    def top_index(row, col):
        return row * cols + col

    def bottom_index(row, col):
        return bottom_offset + row * cols + col

    # Top surface
    for row in range(rows - 1):
        for col in range(cols - 1):
            a = top_index(row, col)
            b = top_index(row, col + 1)
            c = top_index(row + 1, col)
            d = top_index(row + 1, col + 1)

            faces.append([3, a, c, b])
            faces.append([3, b, c, d])

    # Bottom surface
    for row in range(rows - 1):
        for col in range(cols - 1):
            a = bottom_index(row, col)
            b = bottom_index(row, col + 1)
            c = bottom_index(row + 1, col)
            d = bottom_index(row + 1, col + 1)

            faces.append([3, a, b, c])
            faces.append([3, b, d, c])

    # Front and back side walls
    for col in range(cols - 1):
        # Top row side
        t1 = top_index(0, col)
        t2 = top_index(0, col + 1)
        b1 = bottom_index(0, col)
        b2 = bottom_index(0, col + 1)

        faces.append([3, t1, t2, b1])
        faces.append([3, t2, b2, b1])

        # Bottom row side
        t1 = top_index(rows - 1, col)
        t2 = top_index(rows - 1, col + 1)
        b1 = bottom_index(rows - 1, col)
        b2 = bottom_index(rows - 1, col + 1)

        faces.append([3, t1, b1, t2])
        faces.append([3, t2, b1, b2])

    # Left and right side walls
    for row in range(rows - 1):
        # Left column side
        t1 = top_index(row, 0)
        t2 = top_index(row + 1, 0)
        b1 = bottom_index(row, 0)
        b2 = bottom_index(row + 1, 0)

        faces.append([3, t1, b1, t2])
        faces.append([3, t2, b1, b2])

        # Right column side
        t1 = top_index(row, cols - 1)
        t2 = top_index(row + 1, cols - 1)
        b1 = bottom_index(row, cols - 1)
        b2 = bottom_index(row + 1, cols - 1)

        faces.append([3, t1, t2, b1])
        faces.append([3, t2, b2, b1])

    faces = np.array(faces, dtype=np.int64).ravel()

    return vertices, faces