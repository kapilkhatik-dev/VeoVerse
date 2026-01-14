"""
Core module for generating single videos using Veo v3.
"""
import sys
import logging
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError as e:
    raise ImportError("google-genai package is required. Install with: pip install google-genai") from e

from config import (
    DEFAULT_MODEL,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_RESOLUTION,
    DEFAULT_DURATION_SECONDS,
    GOOGLE_API_KEY
)
from utils import (
    generate_filename,
    get_output_path,
    poll_operation,
    download_video,
    validate_parameters,
    print_video_info
)

logger = logging.getLogger(__name__)


class VeoVideoGenerator:
    """
    Main class for generating videos using Veo v3 API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the video generator.
        
        Args:
            api_key: Google API key (uses GOOGLE_API_KEY env var if not provided)
        
        Raises:
            ValueError: If API key is not provided
            RuntimeError: If client initialization fails
        """
        self.api_key = api_key or GOOGLE_API_KEY
        if not self.api_key:
            logger.error("API key not provided")
            raise ValueError(
                "API key is required. Set GOOGLE_API_KEY in .env file or pass it to constructor."
            )
        
        # Initialize the client
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("VeoVideoGenerator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client: {e}")
            raise RuntimeError(f"Failed to initialize video generator: {e}") from e
    
    def generate_video(
        self,
        prompt: str,
        model: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        output_filename: Optional[str] = None,
        **kwargs
    ) -> Path:
        """
        Generate a single video from a text prompt.
        
        Args:
            prompt: Text description of the video to generate
            model: Veo model to use (default: veo-3.1-generate-preview)
            aspect_ratio: Video aspect ratio (default: 16:9)
            resolution: Video resolution (default: 720p)
            duration_seconds: Video duration in seconds (default: 8)
            negative_prompt: Elements to exclude from the video
            seed: Random seed for reproducibility
            output_filename: Custom output filename (auto-generated if not provided)
            **kwargs: Additional parameters to pass to the API
        
        Returns:
            Path to the generated video file
        
        Example:
            >>> generator = VeoVideoGenerator()
            >>> video_path = generator.generate_video(
            ...     prompt="A cinematic shot of a futuristic city",
            ...     resolution="1080p"
            ... )
        """
        # Validate prompt
        if not prompt or not isinstance(prompt, str):
            logger.error("Invalid prompt provided")
            raise ValueError("Prompt must be a non-empty string")
        
        if len(prompt.strip()) == 0:
            logger.error("Empty prompt provided")
            raise ValueError("Prompt cannot be empty or whitespace only")
        
        # Use defaults for unspecified parameters
        model = model or DEFAULT_MODEL
        aspect_ratio = aspect_ratio or DEFAULT_ASPECT_RATIO
        resolution = resolution or DEFAULT_RESOLUTION
        duration_seconds = duration_seconds or DEFAULT_DURATION_SECONDS
        
        # Validate parameters
        try:
            validate_parameters(aspect_ratio, resolution, duration_seconds, model)
        except ValueError as e:
            logger.error(f"Parameter validation failed: {e}")
            raise
        
        logger.info(f"Starting video generation with model: {model}")
        logger.info(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        logger.info(f"Aspect Ratio: {aspect_ratio}, Resolution: {resolution}, Duration: {duration_seconds}s")
        
        try:
            # Build configuration
            config_params: Dict[str, Any] = {
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "duration_seconds": duration_seconds,
            }
            
            if negative_prompt:
                config_params["negative_prompt"] = negative_prompt
            
            if seed is not None:
                config_params["seed"] = seed
            
            # Add any additional kwargs
            config_params.update(kwargs)
            
            config = types.GenerateVideosConfig(**config_params)
            
            # Start video generation
            logger.info("Submitting video generation request to API")
            operation = self.client.models.generate_videos(
                model=model,
                prompt=prompt,
                config=config
            )
            
            # Poll until complete
            operation = poll_operation(self.client, operation)
            
            # Download the video
            if not operation.response or not operation.response.generated_videos:
                logger.error("No videos generated in response")
                raise RuntimeError("API did not return any generated videos")
            
            generated_video = operation.response.generated_videos[0]
            
            # Generate output filename if not provided
            if not output_filename:
                output_filename = generate_filename(prompt, model)
            
            output_path = get_output_path(output_filename)
            download_video(self.client, generated_video.video, output_path)
            
            # Print video info
            print_video_info(output_path)
            
            logger.info(f"Video generation completed successfully: {output_path}")
            return output_path
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            raise
        except TimeoutError as e:
            logger.error(f"Generation timeout: {e}")
            raise
        except RuntimeError as e:
            logger.error(f"Runtime error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during video generation: {e}")
            raise RuntimeError(f"Video generation failed: {e}") from e
    
    def generate_video_with_image(
        self,
        prompt: str,
        image_path: str,
        model: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        output_filename: Optional[str] = None,
        **kwargs
    ) -> Path:
        """
        Generate a video from a text prompt and starting image.
        
        Args:
            prompt: Text description of the video to generate
            image_path: Path to the image to use as the first frame
            model: Veo model to use
            aspect_ratio: Video aspect ratio
            resolution: Video resolution
            duration_seconds: Video duration in seconds
            output_filename: Custom output filename
            **kwargs: Additional parameters
        
        Returns:
            Path to the generated video file
        
        Raises:
            ValueError: If parameters are invalid
            FileNotFoundError: If image file doesn't exist
            RuntimeError: If generation fails
        """
        # Validate prompt
        if not prompt or not isinstance(prompt, str) or len(prompt.strip()) == 0:
            logger.error("Invalid prompt provided")
            raise ValueError("Prompt must be a non-empty string")
        
        # Validate image path
        if not image_path or not isinstance(image_path, str):
            logger.error("Invalid image path provided")
            raise ValueError("Image path must be a non-empty string")
        
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            logger.error(f"Image file not found: {image_path}")
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if not image_path_obj.is_file():
            logger.error(f"Image path is not a file: {image_path}")
            raise ValueError(f"Image path is not a file: {image_path}")
        
        try:
            from PIL import Image
        except ImportError as e:
            logger.error("PIL/Pillow not installed")
            raise ImportError("PIL/Pillow is required for image-to-video. Install with: pip install Pillow") from e
        
        # Use defaults for unspecified parameters
        model = model or DEFAULT_MODEL
        aspect_ratio = aspect_ratio or DEFAULT_ASPECT_RATIO
        resolution = resolution or DEFAULT_RESOLUTION
        duration_seconds = duration_seconds or DEFAULT_DURATION_SECONDS
        
        try:
            validate_parameters(aspect_ratio, resolution, duration_seconds, model)
        except ValueError as e:
            logger.error(f"Parameter validation failed: {e}")
            raise
        
        logger.info(f"Starting image-to-video generation with image: {image_path}")
        logger.info(f"Model: {model}")
        logger.info(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        
        try:
            # Load image
            image = Image.open(image_path)
            logger.info(f"Image loaded successfully: {image.size}")
            
            # Build configuration
            config_params: Dict[str, Any] = {
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "duration_seconds": duration_seconds,
            }
            config_params.update(kwargs)
            config = types.GenerateVideosConfig(**config_params)
            
            # Start video generation with image
            logger.info("Submitting image-to-video request to API")
            operation = self.client.models.generate_videos(
                model=model,
                prompt=prompt,
                image=image,
                config=config
            )
            
            # Poll until complete
            operation = poll_operation(self.client, operation)
            
            # Download the video
            if not operation.response or not operation.response.generated_videos:
                logger.error("No videos generated in response")
                raise RuntimeError("API did not return any generated videos")
            
            generated_video = operation.response.generated_videos[0]
            
            if not output_filename:
                output_filename = generate_filename(f"img2vid_{prompt}", model)
            
            output_path = get_output_path(output_filename)
            download_video(self.client, generated_video.video, output_path)
            
            print_video_info(output_path)
            
            logger.info(f"Image-to-video generation completed: {output_path}")
            return output_path
            
        except (ValueError, FileNotFoundError) as e:
            raise
        except TimeoutError as e:
            logger.error(f"Generation timeout: {e}")
            raise
        except RuntimeError as e:
            logger.error(f"Runtime error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during image-to-video generation: {e}")
            raise RuntimeError(f"Image-to-video generation failed: {e}") from e


def main():
    """CLI entry point for video generation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate AI videos using Veo v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python veo_generator.py "A cinematic shot of a lion in the savannah"
  python veo_generator.py "Futuristic city" --model veo-3.1-fast-generate-preview
  python veo_generator.py "Sunset beach" --resolution 1080p --duration 8
  python veo_generator.py "Mountain landscape" --image input.jpg
        """
    )
    
    parser.add_argument('prompt', nargs='*', help='Text description of the video to generate')
    parser.add_argument('-m', '--model', help='Veo model to use (default: veo-3.1-generate-preview)')
    parser.add_argument('-a', '--aspect-ratio', choices=['16:9', '9:16'], help='Video aspect ratio (default: 16:9)')
    parser.add_argument('-r', '--resolution', choices=['720p', '1080p'], help='Video resolution (default: 720p)')
    parser.add_argument('-d', '--duration', type=int, choices=[4, 6, 8], help='Video duration in seconds (default: 8)')
    parser.add_argument('-n', '--negative-prompt', help='Elements to exclude from the video')
    parser.add_argument('-s', '--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('-o', '--output', help='Custom output filename')
    parser.add_argument('-i', '--image', help='Input image path for image-to-video generation')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate prompt
    if not args.prompt:
        parser.print_help()
        sys.exit(1)
    
    prompt = " ".join(args.prompt)
    
    try:
        generator = VeoVideoGenerator()
        
        logger.info("="*60)
        logger.info("VEO VIDEO GENERATION")
        logger.info("="*60)
        
        if args.image:
            video_path = generator.generate_video_with_image(
                prompt=prompt,
                image_path=args.image,
                model=args.model,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution,
                duration_seconds=args.duration,
                output_filename=args.output
            )
        else:
            video_path = generator.generate_video(
                prompt=prompt,
                model=args.model,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution,
                duration_seconds=args.duration,
                negative_prompt=args.negative_prompt,
                seed=args.seed,
                output_filename=args.output
            )
        
        logger.info("="*60)
        logger.info(f"✓ SUCCESS! Video saved to: {video_path}")
        logger.info("="*60)
        return 0
        
    except Exception as e:
        logger.error("="*60)
        logger.error(f"✗ ERROR: {e}")
        logger.error("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
