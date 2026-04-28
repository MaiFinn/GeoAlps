import rasterio
import os
import numpy as np

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

def sanity_checks(dataset):

    return #sanity check successful? Yes/No -> if No - what was wrong?

if __name__ == "__main__":

    print("I only run when executed directly.")

    data_path = "topographic_data/output_hh.tif"

    dataset = load_raster(data_path)

    inspect_raster(dataset)
