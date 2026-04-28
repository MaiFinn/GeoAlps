# 1.) Load data
# 2.) Sanity checks
# 3.) Optional inspection
# 4.) Select crop area
# 5.) Crop raster
# 6.) Load cropped raster
# 7.) Render cropped raster as detailed 3D terrain

from pathlib import Path
import logging

from src.config.logging_config import setup_logging
from src.io.sanity_checks import sanity_checks
from src.io.load_topo_data import load_raster, inspect_raster
from src.mesh.raster_to_mesh import raster_band_to_mesh
from src.visualization.plot_mesh import plot_terrain_mesh
from src.visualization.plot_mesh_pyvista import plot_terrain_3d
from src.visualization.plot_raster_2d import plot_raster_2d
from src.visualization.select_crop_area import select_crop_area_2d
from src.processing.cropping import crop_raster_by_bounds


logger = logging.getLogger(__name__)


def main():
    project_root = Path(__file__).resolve().parents[1]

    setup_logging(
        log_dir=project_root / "logs",
        log_level=logging.INFO,
        log_to_file=True,
    )

    path = project_root / "topographic_data" / "output_hh.tif"

    # Available modes:
    # "2d"          -> show 2D raster preview
    # "matplotlib"  -> show downsampled matplotlib 3D preview
    # "2d_select"   -> select crop area and render cropped area in 3D
    plot = "2d_select"

    logger.info("Loading raster from: %s", path)

    try:
        dataset = load_raster(path)

        logger.info("Running sanity checks.")
        check_result = sanity_checks(dataset)

        if not check_result["success"]:
            logger.error("Stopping pipeline because sanity checks failed.")

            for error in check_result["errors"]:
                logger.error("Sanity check error: %s", error)

            for key, value in check_result["summary"].items():
                logger.error("Dataset summary | %s: %s", key, value)

            raise ValueError("Sanity checks failed. See log output for details.")

        logger.info("Sanity checks passed.")

        logger.info("Inspecting raster.")
        inspect_raster(dataset)

        logger.info("Reading band 1.")
        band = dataset.read(1)
        logger.info("Band 1 loaded. Shape=%s, dtype=%s", band.shape, band.dtype)

        if plot == "matplotlib":
            logger.info("Creating downsampled mesh for matplotlib preview.")

            x_grid, y_grid, z_grid = raster_band_to_mesh(
                dataset=dataset,
                band=band,
                downsample_factor=25,
            )

            plot_terrain_mesh(
                x_grid=x_grid,
                y_grid=y_grid,
                z_grid=z_grid,
                z_scale=0.1,
                title="Alpine Terrain Mesh",
                scale_reference="min",
                fix_z_axis=True,
            )

        elif plot == "2d":
            logger.info("Showing 2D raster preview.")

            plot_raster_2d(
                dataset=dataset,
                band=band,
                title="Alpine Topography Preview",
            )

        elif plot == "2d_select":
            logger.info("Starting crop area selection.")

            crop_bounds = select_crop_area_2d(
                dataset=dataset,
                band=band,
                title="Select Alpine Crop Area",
            )

            if crop_bounds is None:
                logger.warning("No crop bounds selected. Stopping pipeline.")
                return

            logger.info("Selected crop bounds: %s", crop_bounds)

            output_path = project_root / "outputs" / "cropped_terrain.tif"

            cropped_path, cropped_data = crop_raster_by_bounds(
                dataset=dataset,
                crop_bounds=crop_bounds,
                output_path=output_path,
            )

            logger.info("Cropped raster saved to: %s", cropped_path)
            logger.info("Cropped raster shape: %s", cropped_data.shape)

            logger.info("Loading cropped raster for detailed 3D rendering.")
            cropped_dataset = load_raster(cropped_path)

            logger.info("Reading cropped raster band 1.")
            cropped_band = cropped_dataset.read(1)
            logger.info(
                "Cropped band loaded. Shape=%s, dtype=%s",
                cropped_band.shape,
                cropped_band.dtype,
            )

            logger.info("Creating full-resolution mesh from cropped raster.")

            cropped_x_grid, cropped_y_grid, cropped_z_grid = raster_band_to_mesh(
                dataset=cropped_dataset,
                band=cropped_band,
                downsample_factor=1,
            )

            logger.info("Rendering cropped terrain in 3D.")

            plot_terrain_3d(
                x_grid=cropped_x_grid,
                y_grid=cropped_y_grid,
                z_grid=cropped_z_grid,
                z_scale=1.5,
                title="Cropped Alpine Terrain 3D Render",
                colormap_name="terrain",
                show_edges=False,
                show_grid=True,
            )

            cropped_dataset.close()

        else:
            logger.error("Unknown plot mode: %s", plot)
            raise ValueError(f"Unknown plot mode: {plot}")

        dataset.close()

    except Exception:
        logger.exception("GeoAlps pipeline failed.")
        raise

    logger.info("GeoAlps pipeline finished successfully.")


if __name__ == "__main__":
    main()