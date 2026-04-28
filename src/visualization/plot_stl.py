import logging
from pathlib import Path

import pyvista as pv


logger = logging.getLogger(__name__)


def plot_stl_model(
    stl_path,
    title="STL Model Preview",
    show_edges=True,
    show_grid=True,
    color="lightgray",
):
    """
    Load and render an STL file for final visual inspection.

    Parameters
    ----------
    stl_path : str | Path
        Path to the STL file.
    title : str
        Window title.
    show_edges : bool
        If True, show triangle edges.
    show_grid : bool
        If True, show a coordinate grid.
    color : str
        Surface color used for the STL model.

    Raises
    ------
    FileNotFoundError
        If the STL file does not exist.
    ValueError
        If the STL mesh is empty.
    """

    stl_path = Path(stl_path)

    logger.info("Loading STL file for preview: %s", stl_path)

    if not stl_path.exists():
        logger.error("STL file not found: %s", stl_path)
        raise FileNotFoundError(f"STL file not found: {stl_path}")

    mesh = pv.read(stl_path)

    if mesh.n_points == 0 or mesh.n_cells == 0:
        logger.error(
            "STL mesh is empty. Points=%s, cells=%s",
            mesh.n_points,
            mesh.n_cells,
        )
        raise ValueError("STL mesh is empty.")

    logger.info(
        "STL loaded successfully. Points=%s, cells=%s, bounds=%s",
        mesh.n_points,
        mesh.n_cells,
        mesh.bounds,
    )

    plotter = pv.Plotter(window_size=(1400, 900))
    plotter.add_text(title, font_size=12)

    plotter.add_mesh(
        mesh,
        color=color,
        show_edges=show_edges,
        smooth_shading=False,
    )

    if show_grid:
        plotter.show_grid(
            xlabel="X [mm]",
            ylabel="Y [mm]",
            zlabel="Z [mm]",
        )
    else:
        plotter.show_axes()

    plotter.view_isometric()

    logger.info("Displaying STL preview.")

    plotter.show(title=title)