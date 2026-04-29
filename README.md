# GeoAlps

GeoAlps is a Python project for loading, inspecting, cropping, visualizing, and exporting raster-based elevation data.

The project focuses on alpine topographic data such as GeoTIFF-based digital elevation models, but the underlying workflow can also be adapted for other raster datasets where pixel values represent a height, intensity, depth, or similar scalar field. This makes the project useful not only for terrain models, but also for other surface-like datasets that can be converted into 3D geometry.

GeoAlps allows users to load a raster file, inspect its metadata, select a crop area from a 2D preview, render the selected area as a 3D surface, and export the result as an STL file for 3D printing.

Solid Open-Source topographic data can be downloaded e.g. from https://dataspace.copernicus.eu with a resolution of up to 30 meters.

## Features

- Load raster data from GeoTIFF files
- Run basic sanity checks on raster datasets
- Inspect raster metadata such as CRS, bounds, transform, width, height, and NoData values
- Display 2D raster previews
- Interactively select a crop area from a 2D view
- Crop the original raster based on selected geographic bounds
- Convert cropped raster data into a mesh
- Render cropped raster data as an interactive 3D surface using PyVista
- Export cropped surfaces as watertight STL files for 3D printing
- Preview exported STL files before printing

## Project Structure

```text
GeoAlps/
├── scripts/
│   └── main.py
├── src/
│   ├── config/
│   │   └── logging_config.py
│   ├── export/
│   │   └── export_stl.py
│   ├── io/
│   │   ├── load_topo_data.py
│   │   └── sanity_checks.py
│   ├── mesh/
│   │   └── raster_to_mesh.py
│   ├── processing/
│   │   └── cropping.py
│   └── visualization/
│       ├── plot_mesh.py
│       ├── plot_mesh_pyvista.py
│       ├── plot_raster_2d.py
│       ├── plot_stl.py
│       └── select_crop_area.py
├── topographic_data/
│   └── .gitkeep
├── outputs/
│   └── .gitkeep
├── logs/
│   └── .gitkeep
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/GeoAlps.git
cd GeoAlps
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage

Place your input GeoTIFF file in the `topographic_data/` directory named as 'output_hh.tif'.

For example:

```text
topographic_data/output_hh.tif
```

Run the main pipeline from the project root:

```bash
python -m scripts.main
```

The current pipeline can:

1. Load the raster file
2. Run sanity checks
3. Open a 2D preview
4. Let the user select a crop area
5. Crop the original raster
6. Render the cropped area in 3D
7. Export the surface as an STL file
8. Preview the exported STL model

## Data Handling

Large raster files are not included in this repository.

The `topographic_data/` directory is intended for local input data and is ignored by Git except for the `.gitkeep` placeholder file.

The `outputs/` directory is used for generated files such as cropped GeoTIFFs and STL exports. It is ignored by Git except for the `.gitkeep` placeholder file.

The `logs/` directory stores log files generated during execution. It is ignored by Git except for the `.gitkeep` placeholder file.

## Main Workflow

The current workflow is implemented in:

```text
scripts/main.py
```

The intended processing sequence is:

```text
Load GeoTIFF
↓
Run sanity checks
↓
Inspect raster metadata
↓
Show 2D crop selection view
↓
Crop original raster
↓
Load cropped raster
↓
Create mesh
↓
Render detailed 3D surface
↓
Export watertight STL
↓
Preview STL file
```

## STL Export

GeoAlps can export raster-derived surfaces as watertight STL files for 3D printing.

The STL export includes:

- top surface
- side walls
- flat bottom base

The export function supports configuration of:

- model size in millimeters
- base thickness
- vertical exaggeration
- coordinate conversion from longitude/latitude to approximate local meters

Example parameters:

```python
target_size_mm = 120.0
base_thickness_mm = 3.0
z_exaggeration = 1.5
```

STL files do not store colors. The colors shown in PyVista are only used for visualization.

## Logging

GeoAlps uses Python logging to make processing steps and errors easier to trace.

Logs are written to:

```text
logs/geoalps.log
```

The logging setup is defined in:

```text
src/config/logging_config.py
```

## Development Notes

The project is designed as a modular Python codebase.

Core functionality is separated into reusable modules:

- `src/io/` for loading and checking raster data
- `src/processing/` for cropping and data processing
- `src/mesh/` for mesh generation
- `src/visualization/` for 2D, 3D, and STL previews
- `src/export/` for STL export
- `src/config/` for logging and configuration

This structure keeps the processing logic independent from the user interface and makes it easier to reuse the core functionality in different workflows.

## Requirements

The project depends mainly on:

- `numpy`
- `rasterio`
- `matplotlib`
- `pyvista`

Exact package versions are listed in:

```text
requirements.txt
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
