import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os


def load_raster(file_path):
    """Lädt Rasterdatei + grundlegende Checks."""
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Datei nicht gefunden: {file_path}")
    
    dataset = rasterio.open(file_path)
    
    if dataset.count < 1:
        raise ValueError("Raster hat keine Bänder.")
    
    if dataset.width == 0 or dataset.height == 0:
        raise ValueError("Ungültige Rasterdimensionen.")
    
    return dataset


def inspect_raster(dataset):
    """Gibt wichtige Metadaten aus."""
    
    print("\n=== Raster Informationen ===")
    print(f"Breite x Höhe: {dataset.width} x {dataset.height}")
    print(f"Anzahl Bänder: {dataset.count}")
    print(f"CRS: {dataset.crs}")
    print(f"Transform: {dataset.transform}")
    print(f"NoData Wert: {dataset.nodata}")
    
    band = dataset.read(1)
    
    print("\n=== Statistik ===")
    print(f"Min: {np.nanmin(band)}")
    print(f"Max: {np.nanmax(band)}")
    print(f"Mean: {np.nanmean(band):.2f}")
    print(f"Std: {np.nanstd(band):.2f}")
    
    return band


def clean_band(band, dataset):
    """Entfernt NoData sauber."""
    
    if dataset.nodata is not None:
        band = np.where(band == dataset.nodata, np.nan, band)
    
    return band


def plot_exact_2d(band):
    """Pixelgenaue Darstellung."""
    
    plt.figure(figsize=(8, 6))
    
    plt.imshow(
        band,
        cmap='terrain',
        interpolation='nearest'
    )
    
    plt.colorbar(label='Höhe')
    plt.title("Exakte Höhenmatrix (2D)")
    
    plt.tight_layout()
    plt.show()


def plot_histogram(band):
    """Höhenverteilung."""
    
    plt.figure(figsize=(6, 4))
    
    valid = band[~np.isnan(band)]
    
    plt.hist(valid, bins=100)
    
    plt.title("Höhenverteilung")
    plt.xlabel("Höhe")
    plt.ylabel("Häufigkeit")
    
    plt.tight_layout()
    plt.show()


def compute_z_stats(band):
    """Berechnet robuste Höhenstatistik."""
    
    valid = band[~np.isnan(band)]
    
    z_min = np.percentile(valid, 1)
    z_max = np.percentile(valid, 99)
    z_range = z_max - z_min
    
    print("\n=== Robuste Höhenwerte (1–99%) ===")
    print(f"Min (1%): {z_min}")
    print(f"Max (99%): {z_max}")
    print(f"Range: {z_range}")
    
    return z_min, z_max, z_range


def suggest_z_scale(band, target_ratio=0.2):
    """
    Vorschlag für Z-Skalierung.
    
    target_ratio:
    Verhältnis Höhe / Breite (z.B. 0.2 = 20%)
    """
    
    rows, cols = band.shape
    xy_size = max(rows, cols)
    
    _, _, z_range = compute_z_stats(band)
    
    z_scale = (xy_size * target_ratio) / z_range
    
    print(f"\nEmpfohlene Z-Skalierung: {z_scale:.3f}")
    
    return z_scale


def plot_exact_3d(band, z_scale=1.0):
    """3D Vorschau mit korrekter visueller Skalierung."""
    
    rows, cols = band.shape
    
    x, y = np.meshgrid(
        np.arange(cols),
        np.arange(rows)
    )
    
    z = band * z_scale
    
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(
        x, y, z,
        cmap='terrain',
        linewidth=0,
        antialiased=False,
        shade=False
    )
    
    ax.set_box_aspect([cols, rows, z_scale * (np.nanmax(band) - np.nanmin(band))])
    
    fig.colorbar(surf, shrink=0.5, label="Höhe")
    
    ax.set_title(f"3D Mesh Preview (z_scale={z_scale:.2f})")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Höhe")
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    
    print("=== Starte Analyse ===")
    
    raster_file = "../topographic_data/output_hh.tif"
    
    # Laden
    dataset = load_raster(raster_file)
    
    # Analyse
    band = inspect_raster(dataset)
    
    # Clean
    band = clean_band(band, dataset)
    
    # Visualisierung
    plot_exact_2d(band)
    plot_histogram(band)
    
    # 3D Plot mit Vorschlag
    plot_exact_3d(band, z_scale=0.05)
    
    
    print("\n=== Analyse abgeschlossen ===")