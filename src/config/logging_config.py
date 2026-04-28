import logging
from pathlib import Path


def setup_logging(
    log_dir: Path,
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    ) -> None:
    """
    Zentrale Logging-Konfiguration für GeoAlps.

    Parameters
    ----------
    log_dir : Path
        Ordner, in dem Log-Dateien gespeichert werden.
    log_level : int
        Logging-Level, z. B. logging.INFO oder logging.DEBUG.
    log_to_file : bool
        Ob zusätzlich in eine Datei geloggt werden soll.
    """

    log_dir.mkdir(parents=True, exist_ok=True)

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(filename)s:%(lineno)d | %(message)s"
    )

    handlers = [
        logging.StreamHandler()
    ]

    if log_to_file:
        log_file = log_dir / "geoalps.log"
        handlers.append(logging.FileHandler(log_file, mode="a", encoding="utf-8"))

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
        force=True,
    )