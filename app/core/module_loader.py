# app/core/module_loader.py

import pkgutil
import importlib
from pathlib import Path

from app.core.logger import logger


def load_modules():
    package = "app.modules"
    modules_path = str(Path(__file__).resolve().parent.parent / "modules")

    for _, module_name, _ in pkgutil.walk_packages([modules_path]):
        full_name = f"{package}.{module_name}"
        try:
            importlib.import_module(full_name)
            logger.info(f"Loaded module: {full_name}")
        except Exception as e:
            logger.warning(f"Failed to load module {full_name}: {e}")
