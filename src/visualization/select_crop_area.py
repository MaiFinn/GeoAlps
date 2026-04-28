import logging

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import RectangleSelector


logger = logging.getLogger(__name__)


def select_crop_area_2d(dataset, band, title="Select Crop Area"):
    """
    Display a 2D raster preview and allow the user to select a crop area.

    Parameters
    ----------
    dataset : rasterio.io.DatasetReader
        Open rasterio dataset.
    band : np.ndarray
        2D raster band array.
    title : str
        Plot title.

    Returns
    -------
    dict | None
        Selected crop bounds as a dictionary:
        {
            "left": float,
            "right": float,
            "bottom": float,
            "top": float
        }

        Returns None if no crop area was selected.
    """

    logger.info("Opening 2D crop area selector.")

    if dataset is None:
        logger.error("Dataset is None.")
        raise ValueError("Dataset must not be None.")

    if band is None:
        logger.error("Band is None.")
        raise ValueError("Band must not be None.")

    if band.ndim != 2:
        logger.error("Band must be a 2D array. Got shape: %s", band.shape)
        raise ValueError(f"Band must be a 2D array. Got shape: {band.shape}")

    nodata = getattr(dataset, "nodata", None)
    bounds = dataset.bounds

    band_plot = band.astype("float64", copy=False)

    if nodata is not None:
        band_plot = np.where(band_plot == nodata, np.nan, band_plot)

    extent = [
        bounds.left,
        bounds.right,
        bounds.bottom,
        bounds.top,
    ]

    selected_bounds = {"value": None}

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

    def on_select(click_event, release_event):
        """
        Store crop bounds after the user draws a rectangle.
        """

        x1, y1 = click_event.xdata, click_event.ydata
        x2, y2 = release_event.xdata, release_event.ydata

        if None in (x1, y1, x2, y2):
            logger.warning("Crop selection ignored because it is outside the plot area.")
            return

        left = min(x1, x2)
        right = max(x1, x2)
        bottom = min(y1, y2)
        top = max(y1, y2)

        selected_bounds["value"] = {
            "left": float(left),
            "right": float(right),
            "bottom": float(bottom),
            "top": float(top),
        }

        logger.info(
            "Selected crop bounds: left=%s, right=%s, bottom=%s, top=%s",
            left,
            right,
            bottom,
            top,
        )

    selector = RectangleSelector(
        ax=ax,
        onselect=on_select,
        useblit=True,
        button=[1],
        minspanx=0.0,
        minspany=0.0,
        spancoords="data",
        interactive=True,
    )

    ax.text(
        0.01,
        0.01,
        "Draw a rectangle with the left mouse button.\nClose the window to confirm selection.",
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment="bottom",
        bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"},
    )

    plt.tight_layout()
    plt.show()

    # Keep a reference so the selector does not get garbage-collected.
    _ = selector

    if selected_bounds["value"] is None:
        logger.warning("No crop area was selected.")
        return None

    logger.info("Crop area selection finished successfully.")

    return selected_bounds["value"]