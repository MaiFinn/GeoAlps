import logging

import numpy as np


logger = logging.getLogger(__name__)


def raster_band_to_mesh(dataset, band, downsample_factor=10):
    """
    Convert a raster band into x, y, z arrays for terrain mesh visualization.

    Parameters
    ----------
    dataset : rasterio.io.DatasetReader
        Open rasterio dataset containing raster metadata and transform.
    band : np.ndarray
        2D raster band array containing elevation values.
    downsample_factor : int
        Factor used to reduce the raster resolution for faster visualization.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        x_grid, y_grid, and z_grid arrays representing the terrain surface.

    Raises
    ------
    ValueError
        If the input band is invalid or the downsample factor is not valid.
    """

    logger.info("Converting raster band to terrain mesh.")

    if dataset is None:
        logger.error("Dataset is None.")
        raise ValueError("Dataset must not be None.")

    if band is None:
        logger.error("Band is None.")
        raise ValueError("Band must not be None.")

    if band.ndim != 2:
        logger.error("Band must be a 2D array. Got shape: %s", band.shape)
        raise ValueError(f"Band must be a 2D array. Got shape: {band.shape}")

    if downsample_factor < 1:
        logger.error("Invalid downsample factor: %s", downsample_factor)
        raise ValueError("downsample_factor must be greater than or equal to 1.")

    logger.info("Input band shape: %s", band.shape)
    logger.info("Downsample factor: %s", downsample_factor)

    band_downsampled = band[::downsample_factor, ::downsample_factor]

    if band_downsampled.size == 0:
        logger.error("Downsampled band is empty.")
        raise ValueError("Downsampled band is empty.")

    rows, cols = band_downsampled.shape

    row_indices = np.arange(0, band.shape[0], downsample_factor)[:rows]
    col_indices = np.arange(0, band.shape[1], downsample_factor)[:cols]

    col_grid, row_grid = np.meshgrid(col_indices, row_indices)

    x_grid, y_grid = dataset.transform * (col_grid, row_grid)

    z_grid = band_downsampled.astype("float64", copy=False)

    nodata = getattr(dataset, "nodata", None)

    if nodata is not None:
        logger.info("Replacing NoData values with NaN. NoData value: %s", nodata)
        z_grid = np.where(z_grid == nodata, np.nan, z_grid)
    else:
        logger.info("No NoData value defined. Keeping all finite elevation values.")

    valid_z_count = int(np.count_nonzero(np.isfinite(z_grid)))
    total_z_count = int(z_grid.size)

    logger.info(
        "Terrain mesh created. Shape=%s, valid_z_values=%s, invalid_z_values=%s",
        z_grid.shape,
        valid_z_count,
        total_z_count - valid_z_count,
    )

    return x_grid, y_grid, z_grid