"""
Module for discovering and listing available Veo models.
"""
from typing import List, Dict, Optional
from google import genai

from config import GOOGLE_API_KEY, SUPPORTED_MODELS


class ModelInfo:
    """Information about a Veo model."""
    
    def __init__(
        self,
        name: str,
        description: str,
        supported_modalities: List[str],
        resolution: str,
        duration: str,
        audio: bool,
        status: str
    ):
        self.name = name
        self.description = description
        self.supported_modalities = supported_modalities
        self.resolution = resolution
        self.duration = duration
        self.audio = audio
        self.status = status
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "supported_modalities": self.supported_modalities,
            "resolution": self.resolution,
            "duration": self.duration,
            "audio": self.audio,
            "status": self.status
        }
    
    def __str__(self) -> str:
        return (
            f"Model: {self.name}\n"
            f"  Description: {self.description}\n"
            f"  Modalities: {', '.join(self.supported_modalities)}\n"
            f"  Resolution: {self.resolution}\n"
            f"  Duration: {self.duration}\n"
            f"  Audio: {'Yes' if self.audio else 'No'}\n"
            f"  Status: {self.status}"
        )


# Static model information based on documentation
KNOWN_MODELS = [
    ModelInfo(
        name="veo-3.1-generate-preview",
        description="Veo 3.1 Preview - State-of-the-art video generation with audio, supports video extension and reference images",
        supported_modalities=["Text-to-Video", "Image-to-Video", "Video-to-Video"],
        resolution="720p & 1080p (8s only)",
        duration="4s, 6s, 8s",
        audio=True,
        status="Preview"
    ),
    ModelInfo(
        name="veo-3.1-fast-generate-preview",
        description="Veo 3.1 Fast Preview - Optimized for speed while maintaining high quality, ideal for rapid content generation",
        supported_modalities=["Text-to-Video", "Image-to-Video", "Video-to-Video"],
        resolution="720p & 1080p (8s only)",
        duration="4s, 6s, 8s",
        audio=True,
        status="Preview"
    ),
    ModelInfo(
        name="veo-3.0-generate-001",
        description="Veo 3 Stable - High-quality video generation with native audio support",
        supported_modalities=["Text-to-Video", "Image-to-Video"],
        resolution="720p & 1080p (16:9 only)",
        duration="4s, 6s, 8s",
        audio=True,
        status="Stable"
    ),
    ModelInfo(
        name="veo-3.0-fast-generate-001",
        description="Veo 3 Fast Stable - Speed-optimized version for business use cases",
        supported_modalities=["Text-to-Video", "Image-to-Video"],
        resolution="720p & 1080p (16:9 only)",
        duration="4s, 6s, 8s",
        audio=True,
        status="Stable"
    ),
    ModelInfo(
        name="veo-2.0-generate-001",
        description="Veo 2 Stable - Previous generation model, silent videos only",
        supported_modalities=["Text-to-Video", "Image-to-Video"],
        resolution="720p",
        duration="5s, 6s, 8s",
        audio=False,
        status="Stable"
    )
]


def list_available_models(api_key: Optional[str] = None) -> List[ModelInfo]:
    """
    List all available Veo models.
    
    Args:
        api_key: Google API key (uses GOOGLE_API_KEY env var if not provided)
    
    Returns:
        List of ModelInfo objects
    
    Example:
        >>> models = list_available_models()
        >>> for model in models:
        ...     print(model)
    """
    # Return the known models from documentation
    # In a future enhancement, this could query the API directly
    return KNOWN_MODELS


def get_model_info(model_name: str, api_key: Optional[str] = None) -> Optional[ModelInfo]:
    """
    Get information about a specific model.
    
    Args:
        model_name: Name of the model
        api_key: Google API key
    
    Returns:
        ModelInfo object or None if not found
    
    Example:
        >>> info = get_model_info("veo-3.1-generate-preview")
        >>> print(info)
    """
    models = list_available_models(api_key)
    for model in models:
        if model.name == model_name:
            return model
    return None


def print_all_models(api_key: Optional[str] = None, use_logger: bool = False) -> None:
    """
    Print information about all available models.
    
    Args:
        api_key: Google API key
        use_logger: If True, use logger instead of print
    """
    import logging
    logger = logging.getLogger(__name__)
    
    models = list_available_models(api_key)
    
    if use_logger:
        logger.info("="*80)
        logger.info(f"Available Veo Models ({len(models)} total)")
        logger.info("="*80)
        
        for i, model in enumerate(models, 1):
            logger.info(f"{i}. {model}")
        
        logger.info("="*80)
    else:
        print(f"\n{'='*80}")
        print(f"Available Veo Models ({len(models)} total)")
        print(f"{'='*80}\n")
        
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")
            print()
        
        print(f"{'='*80}\n")


def get_recommended_model(use_case: str = "general") -> ModelInfo:
    """
    Get a recommended model based on use case.
    
    Args:
        use_case: One of "general", "fast", "quality", "extension"
    
    Returns:
        Recommended ModelInfo object
    
    Example:
        >>> model = get_recommended_model("quality")
        >>> print(f"Recommended: {model.name}")
    """
    recommendations = {
        "general": "veo-3.1-generate-preview",
        "fast": "veo-3.1-fast-generate-preview",
        "quality": "veo-3.1-generate-preview",
        "extension": "veo-3.1-generate-preview",
        "stable": "veo-3.0-generate-001"
    }
    
    model_name = recommendations.get(use_case, "veo-3.1-generate-preview")
    return get_model_info(model_name)


def main():
    """CLI entry point for model discovery."""
    import argparse
    import sys as sys_module
    
    parser = argparse.ArgumentParser(
        description="Discover and list available Veo v3 models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python model_discovery.py
  python model_discovery.py --model veo-3.1-generate-preview
  python model_discovery.py --recommend fast
  python model_discovery.py --list-use-cases
        """
    )
    
    parser.add_argument('-m', '--model', help='Get information about a specific model')
    parser.add_argument('-r', '--recommend', 
                       choices=['general', 'fast', 'quality', 'extension', 'stable'],
                       help='Get recommended model for a use case')
    parser.add_argument('-l', '--list-use-cases', action='store_true',
                       help='List recommendations for all use cases')
    
    args = parser.parse_args()
    
    try:
        if args.model:
            # Show specific model info
            model_info = get_model_info(args.model)
            if model_info:
                print(f"\n{model_info}\n")
            else:
                print(f"Model '{args.model}' not found.")
                return 1
                
        elif args.recommend:
            # Show recommendation
            model = get_recommended_model(args.recommend)
            print(f"\nRecommended model for '{args.recommend}' use case:")
            print(f"\n{model}\n")
            
        elif args.list_use_cases:
            # Show all recommendations
            print("\n" + "="*80)
            print("Recommended Models by Use Case")
            print("="*80 + "\n")
            
            for use_case in ["general", "fast", "quality", "extension", "stable"]:
                model = get_recommended_model(use_case)
                print(f"{use_case.upper()}:")
                print(f"  {model.name} - {model.description}\n")
            
            print("="*80 + "\n")
        else:
            # List all models
            print_all_models()
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
