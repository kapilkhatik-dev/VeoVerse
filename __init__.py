"""
Veo v3 Video Generation Library

A Python library for generating AI-created videos using Google's Veo v3 model.
"""

from config import __version__

__all__ = [
    'VeoVideoGenerator',
    'VeoVideoExtension',
    'list_available_models',
    'get_model_info',
    '__version__'
]

# Import main classes for convenience
try:
    from veo_generator import VeoVideoGenerator
    from veo_extension import VeoVideoExtension
    from model_discovery import list_available_models, get_model_info
except ImportError:
    # Allow import to succeed even if dependencies aren't installed yet
    pass
