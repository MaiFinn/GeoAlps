import logging
from pathlib import Path

import rasterio
from rasterio.windows import from_bounds


logger = logging.getLogger(__name__)


def crop_raster_by_bounds(dataset, crop_bounds, output_path):
    """
    Crop a raster dataset by geographic bounds and save the result as a GeoTIFF.

    Parameters
    ----------
    dataset : rasterio.io.DatasetReader
        Open rasterio dataset.
    crop_bounds : dict
        Crop bounds with the keys:
        {
            "left": float,
            "right": float,
            "bottom": float,
            "top": float
        }
    output_path : str | Path
        Path where the cropped GeoTIFF should be saved.

    Returns
    -------
    tuple[Path, np.ndarray]
        Output path and cropped raster array.

    Raises
    ------
    ValueError
        If the dataset or crop bounds are invalid.
    """

    logger.info("Starting raster crop by bounds.")

    if dataset is None:
        logger.error("Dataset is None.")
        raise ValueError("Dataset must not be None.")

    if crop_bounds is None:
        logger.error("Crop bounds are None.")
        raise ValueError("Crop bounds must not be None.")

    required_keys = {"left", "right", "bottom", "top"}

    if not required_keys.issubset(crop_bounds):
        logger.error("Crop bounds are missing required keys: %s", crop_bounds)
        raise ValueError(f"Crop bounds must contain keys: {required_keys}")

    left = float(crop_bounds["left"])
    right = float(crop_bounds["right"])
    bottom = float(crop_bounds["bottom"])
    top = float(crop_bounds["top"])

    if left >= right:
        logger.error("Invalid crop bounds: left >= right.")
        raise ValueError("Invalid crop bounds: left must be smaller than right.")

    if bottom >= top:
        logger.error("Invalid crop bounds: bottom >= top.")
        raise ValueError("Invalid crop bounds: bottom must be smaller than top.")

    dataset_bounds = dataset.bounds

    if (
        right <= dataset_bounds.left
        or left >= dataset_bounds.right
        or top <= dataset_bounds.bottom
        or bottom >= dataset_bounds.top
    ):
        logger.error(
            "Crop bounds do not overlap dataset bounds. crop=%s, dataset=%s",
            crop_bounds,
            dataset_bounds,
        )
        raise ValueError("Crop bounds do not overlap dataset bounds.")

    clipped_left = max(left, dataset_bounds.left)
    clipped_right = min(right, dataset_bounds.right)
    clipped_bottom = max(bottom, dataset_bounds.bottom)
    clipped_top = min(top, dataset_bounds.top)

    logger.info(
        "Clipped crop bounds: left=%s, right=%s, bottom=%s, top=%s",
        clipped_left,
        clipped_right,
        clipped_bottom,
        clipped_top,
    )

    window = from_bounds(
        left=clipped_left,
        bottom=clipped_bottom,
        right=clipped_right,
        top=clipped_top,
        transform=dataset.transform,
    )

    window = window.round_offsets().round_lengths()

    cropped_data = dataset.read(window=window)

    if cropped_data.size == 0:
        logger.error("Cropped raster data is empty.")
        raise ValueError("Cropped raster data is empty.")

    cropped_transform = dataset.window_transform(window)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_profile = dataset.profile.copy()
    output_profile.update(
        {
            "height": cropped_data.shape[1],
            "width": cropped_data.shape[2],
            "transform": cropped_transform,
        }
    )

    logger.info(
        "Writing cropped raster. Path=%s, shape=%s",
        output_path,
        cropped_data.shape,
    )

    with rasterio.open(output_path, "w", **output_profile) as dst:
        dst.write(cropped_data)

    logger.info("Raster crop saved successfully: %s", output_path)

    return output_path, cropped_data