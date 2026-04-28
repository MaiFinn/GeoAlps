import logging
import numpy as np


logger = logging.getLogger(__name__)


def sanity_checks(dataset):
    """
    Run basic sanity checks for a rasterio dataset.

    Returns
    -------
    dict
        Dictionary containing:
        - success: Whether all critical checks passed.
        - errors: Critical issues that should stop the pipeline.
        - warnings: Non-critical issues that should be reviewed.
        - summary: Basic dataset metadata useful for debugging.
    """

    logger.info("Starting raster sanity checks.")

    errors = []
    warnings = []
    summary = {}

    if dataset is None:
        errors.append("Dataset is None.")
        logger.error("Dataset is None.")

        return {
            "success": False,
            "errors": errors,
            "warnings": warnings,
            "summary": summary,
        }

    if getattr(dataset, "closed", False):
        errors.append("Dataset is closed.")

    width = getattr(dataset, "width", None)
    height = getattr(dataset, "height", None)
    count = getattr(dataset, "count", None)
    crs = getattr(dataset, "crs", None)
    nodata = getattr(dataset, "nodata", None)

    summary["width"] = width
    summary["height"] = height
    summary["band_count"] = count
    summary["crs"] = str(crs) if crs else None
    summary["nodata"] = nodata

    if not width or width <= 0:
        errors.append(f"Invalid raster width: {width}")

    if not height or height <= 0:
        errors.append(f"Invalid raster height: {height}")

    if not count or count <= 0:
        errors.append(f"No valid raster bands found: count={count}")

    if crs is None:
        warnings.append("No CRS defined.")

    if nodata is None:
        warnings.append("No NoData value defined in Metadata of file.")

    if errors:
        for error in errors:
            logger.error("Sanity check failed: %s", error)

        for warning in warnings:
            logger.warning("Sanity check warning: %s", warning)

        logger.error("Raster sanity checks failed before reading band data.")

        return {
            "success": False,
            "errors": errors,
            "warnings": warnings,
            "summary": summary,
        }

    try:
        band = dataset.read(1)
    except Exception as exc:
        errors.append(f"Could not read band 1: {exc}")
        logger.exception("Could not read band 1.")

        return {
            "success": False,
            "errors": errors,
            "warnings": warnings,
            "summary": summary,
        }

    summary["band_shape"] = band.shape
    summary["band_dtype"] = str(band.dtype)

    if band.size == 0:
        errors.append("Band 1 is empty.")
        logger.error("Band 1 is empty.")

        return {
            "success": False,
            "errors": errors,
            "warnings": warnings,
            "summary": summary,
        }

    band_float = band.astype("float64", copy=False)
    valid_mask = np.isfinite(band_float)

    if nodata is not None:
        valid_mask &= band_float != nodata

    valid_pixels = int(np.count_nonzero(valid_mask))
    total_pixels = int(band.size)

    summary["total_pixels"] = total_pixels
    summary["valid_pixels"] = valid_pixels
    summary["invalid_pixels"] = total_pixels - valid_pixels

    if valid_pixels == 0:
        errors.append("Band 1 contains no valid values. All pixels are NoData, NaN, or Inf.")

    for error in errors:
        logger.error("Sanity check failed: %s", error)

    for warning in warnings:
        logger.warning("Sanity check warning: %s", warning)

    logger.info("Raster sanity checks finished. Success=%s", len(errors) == 0)

    return {
        "success": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
    }