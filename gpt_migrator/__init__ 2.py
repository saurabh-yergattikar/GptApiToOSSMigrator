"""
HarmonyMigrator - Automate migration from OpenAI APIs to local GPT-OSS models.

A tool to seamlessly transition codebases from paid OpenAI API dependencies
to local, offline usage of GPT-OSS models via the Harmony response format.
"""

__version__ = "1.0.0"
__author__ = "HarmonyMigrator Team"
__email__ = "team@harmonymigrator.dev"

from .core.models import (
    APICall,
    ConversionResult,
    MigrationReport,
    ScanResult,
)
from .core.config import Config
from .scanner.scanner import Scanner
from .converter.converter import Converter
from .inference.inference import LocalInference

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "APICall",
    "ConversionResult", 
    "MigrationReport",
    "ScanResult",
    "Config",
    "Scanner",
    "Converter",
    "LocalInference",
] 