import logging

import matplotlib.pyplot as plt
import numpy as np


logger = logging.getLogger(__name__)


def plot_raster_2d(dataset, band, title="Raster Preview"):
    """
    Plot a raster band as a 2D elevation preview.

    Parameters
    ----------
    dataset : rasterio.io.DatasetReader
        Open rasterio dataset.
    band : np.ndarray
        2D raster band array.
    title : str
        Plot title.
    """

    logger.info("Creating 2D raster preview.")

    nodata = getattr(dataset, "nodata", None)

    band_plot = band.astype("float64", copy=False)

    if nodata is not None:
        band_plot = np.where(band_plot == nodata, np.nan, band_plot)

    bounds = dataset.bounds

    extent = [
        bounds.left,
        bounds.right,
        bounds.bottom,
        bounds.top,
    ]

    fig, ax = plt.subplots(figsize=(12, 8))

    image = ax.imshow(
        band_plot,
        extent=extent,
        origin="upper",
        cmap="terrain",
    )

    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    fig.colorbar(image, ax=ax, label="Elevation")

    plt.tight_layout()
    plt.show()