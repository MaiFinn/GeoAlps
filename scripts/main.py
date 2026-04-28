# 1.) Laden der Daten
# 2.) Sanity Checks
# 3.) Statistics und Characteristics
# 4.) Cropping der Daten
# 5.) Plotten 2D: vor und nach dem croppen
# 6.) Z-Value Histogramm
# 7.) Plotten 3D

from pathlib import Path
import logging
from src.config.logging_config import setup_logging
from src.io.load_topo_data import load_raster, inspect_raster
#from src.processing.preprocessing import clean_band
#from src.processing.scaling import suggest_z_scale
#from src.visualization.plot_3d import plot_3d


logger = logging.getLogger(__name__)

def main():

    project_root = Path(__file__).resolve().parents[1]

    setup_logging(
        log_dir=project_root / "logs",
        log_level=logging.INFO,
        log_to_file=True,
    )

    path = project_root / "topographic_data/output_hh.tif"

    logger.info("Loading raster from: %s", path)
    
    try:

        dataset = load_raster(path)
        logger.info("Inspecting raster.")

        inspect_raster(dataset)
        logger.info("Reading band 1.")

        band = dataset.read(1)
        logger.info("Band 1 loaded. Shape=%s, dtype=%s", band.shape, band.dtype)

        # band = clean_band(band, dataset.nodata)
        # z_scale = suggest_z_scale(band)
        # plot_3d(band, z_scale)

    except Exception:

        logger.exception("GeoAlps pipeline failed.")

        raise

    logger.info("GeoAlps pipeline finished successfully.")

if __name__ == "__main__":
    main()