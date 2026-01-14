"""
Module for extending videos scene-by-scene using Veo v3.
"""
import sys
import json
import logging
from typing import List, Dict, Any, Optional
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
    GOOGLE_API_KEY,
    EXTENSION_DURATION,
    MAX_EXTENSIONS,
    MAX_INPUT_VIDEO_LENGTH
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


class VeoVideoExtension:
    """
    Class for creating extended videos scene-by-scene.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the video extension handler.
        
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
            logger.info("VeoVideoExtension initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client: {e}")
            raise RuntimeError(f"Failed to initialize video extension handler: {e}") from e
    
    def generate_scene(
        self,
        prompt: str,
        previous_video: Optional[Any] = None,
        model: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Generate a single scene, optionally extending from a previous video.
        
        Args:
            prompt: Text description of the scene
            previous_video: Video object from previous scene (for extension)
            model: Veo model to use
            aspect_ratio: Video aspect ratio
            resolution: Video resolution
            **kwargs: Additional parameters
        
        Returns:
            Video object from the generated scene
        """
        model = model or DEFAULT_MODEL
        aspect_ratio = aspect_ratio or DEFAULT_ASPECT_RATIO
        resolution = resolution or DEFAULT_RESOLUTION
        
        # For extensions, duration must be 8 seconds and resolution must be 720p
        if previous_video:
            resolution = "720p"
            duration_seconds = 8
            logger.info(f"Extending video with new scene")
            logger.info(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            logger.info(f"Extension adds: {EXTENSION_DURATION}s")
        else:
            duration_seconds = kwargs.get('duration_seconds', 8)
            logger.info(f"Generating initial scene")
            logger.info(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            logger.info(f"Duration: {duration_seconds}s")
        
        validate_parameters(aspect_ratio, resolution, duration_seconds, model)
        
        # Build configuration
        config_params: Dict[str, Any] = {
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "duration_seconds": duration_seconds,
            "number_of_videos": 1
        }
        config_params.update(kwargs)
        config = types.GenerateVideosConfig(**config_params)
        
        # Generate video (with or without extension)
        if previous_video:
            operation = self.client.models.generate_videos(
                model=model,
                prompt=prompt,
                video=previous_video,
                config=config
            )
        else:
            operation = self.client.models.generate_videos(
                model=model,
                prompt=prompt,
                config=config
            )
        
        # Poll until complete
        operation = poll_operation(self.client, operation)
        
        # Return the video object for potential further extension
        return operation.response.generated_videos[0]
    
    def extend_from_scenes(
        self,
        scenes: List[Dict[str, Any]],
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Generate an extended video from a list of scenes.
        
        Each scene is generated sequentially, with each extending the previous one.
        
        Args:
            scenes: List of scene dictionaries, each containing:
                - prompt (required): Text description
                - params (optional): Dict of generation parameters
            output_filename: Custom output filename for final video
        
        Returns:
            Path to the final extended video file
        
        Example:
            >>> extender = VeoVideoExtension()
            >>> scenes = [
            ...     {
            ...         "prompt": "A futuristic city at night",
            ...         "params": {"aspect_ratio": "16:9", "resolution": "1080p"}
            ...     },
            ...     {
            ...         "prompt": "Camera zooms into a window",
            ...         "params": {"aspect_ratio": "16:9"}
            ...     }
            ... ]
            >>> video_path = extender.extend_from_scenes(scenes)
        """
        if not scenes:
            raise ValueError("At least one scene is required")
        
        if len(scenes) > MAX_EXTENSIONS + 1:
            raise ValueError(f"Maximum {MAX_EXTENSIONS + 1} scenes allowed (1 initial + {MAX_EXTENSIONS} extensions)")
        
        logger.info("="*60)
        logger.info(f"Starting scene-based video generation")
        logger.info(f"Total scenes: {len(scenes)}")
        logger.info(f"Estimated final duration: {8 + (len(scenes) - 1) * EXTENSION_DURATION}s")
        logger.info("="*60)
        
        video_object = None
        scene_number = 1
        
        for scene in scenes:
            prompt = scene.get("prompt")
            if not prompt:
                raise ValueError(f"Scene {scene_number} is missing 'prompt' field")
            
            params = scene.get("params", {})
            
            logger.info(f"Processing scene {scene_number}/{len(scenes)}...")
            
            # Generate or extend the scene
            generated_video = self.generate_scene(
                prompt=prompt,
                previous_video=video_object.video if video_object else None,
                **params
            )
            
            video_object = generated_video
            scene_number += 1
        
        # Download the final extended video
        if not output_filename:
            combined_prompt = " -> ".join([s.get("prompt", "")[:30] for s in scenes[:3]])
            output_filename = generate_filename(f"extended_{combined_prompt}", DEFAULT_MODEL)
        
        output_path = get_output_path(output_filename)
        download_video(self.client, video_object.video, output_path)
        
        logger.info("="*60)
        logger.info(f"All scenes processed successfully!")
        logger.info(f"Total scenes: {len(scenes)}")
        logger.info(f"Final video duration: ~{8 + (len(scenes) - 1) * EXTENSION_DURATION}s")
        logger.info("="*60)
        
        print_video_info(output_path)
        
        return output_path
    
    def extend_from_scenes_file(
        self,
        scenes_file: str,
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Generate an extended video from a JSON scenes file.
        
        Args:
            scenes_file: Path to JSON file containing scenes
            output_filename: Custom output filename for final video
        
        Returns:
            Path to the final extended video file
        
        Raises:
            ValueError: If scenes file is invalid or contains invalid data
            FileNotFoundError: If scenes file doesn't exist
            RuntimeError: If video generation fails
        
        Example JSON format:
            {
                "scenes": [
                    {
                        "prompt": "A futuristic city at night",
                        "params": {
                            "aspect_ratio": "16:9",
                            "resolution": "1080p"
                        }
                    },
                    {
                        "prompt": "Camera zooms into a window",
                        "params": {
                            "aspect_ratio": "16:9"
                        }
                    }
                ]
            }
        """
        if not scenes_file or not isinstance(scenes_file, str):
            logger.error("Invalid scenes file path")
            raise ValueError("Scenes file path must be a non-empty string")
        
        scenes_path = Path(scenes_file)
        
        if not scenes_path.exists():
            logger.error(f"Scenes file not found: {scenes_file}")
            raise FileNotFoundError(f"Scenes file not found: {scenes_file}")
        
        if not scenes_path.is_file():
            logger.error(f"Scenes path is not a file: {scenes_file}")
            raise ValueError(f"Scenes path is not a file: {scenes_file}")
        
        logger.info(f"Loading scenes from: {scenes_file}")
        
        try:
            with open(scenes_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in scenes file: {e}")
            raise ValueError(f"Invalid JSON in scenes file: {e}") from e
        except Exception as e:
            logger.error(f"Failed to read scenes file: {e}")
            raise RuntimeError(f"Failed to read scenes file: {e}") from e
        
        if not isinstance(data, dict):
            logger.error("Scenes file must contain a JSON object")
            raise ValueError("Scenes file must contain a JSON object with a 'scenes' array")
        
        scenes = data.get("scenes", [])
        
        if not scenes:
            logger.error("No scenes found in the file")
            raise ValueError("No scenes found in the file. Expected a 'scenes' array.")
        
        if not isinstance(scenes, list):
            logger.error("'scenes' must be an array")
            raise ValueError("'scenes' must be an array of scene objects")
        
        return self.extend_from_scenes(scenes, output_filename)
    
    def extend_existing_video(
        self,
        video_path: str,
        extension_prompt: str,
        model: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Extend an existing Veo-generated video with a new prompt.
        
        Args:
            video_path: Path to the existing Veo-generated video
            extension_prompt: Text description for the extension
            model: Veo model to use
            output_filename: Custom output filename
        
        Returns:
            Path to the extended video file
        
        Note:
            - Only Veo-generated videos can be extended
            - Input video must be 720p, 16:9 or 9:16 aspect ratio
            - Maximum input length: 141 seconds
        """
        model = model or DEFAULT_MODEL
        
        logger.info("="*60)
        logger.info(f"Extending existing video...")
        logger.info(f"Input video: {video_path}")
        logger.info(f"Extension prompt: {extension_prompt[:100]}{'...' if len(extension_prompt) > 100 else ''}")
        logger.info("="*60)
        
        # Note: In a real implementation, you would need to load the video properly
        # This is a simplified version showing the API structure
        raise NotImplementedError(
            "Extending pre-existing video files requires uploading the video to the API. "
            "This feature works best when extending videos generated in the same session. "
            "Use extend_from_scenes() to create extended videos scene-by-scene."
        )


def main():
    """CLI entry point for scene-based video extension."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate extended videos scene-by-scene using Veo v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python veo_extension.py scenes.json
  python veo_extension.py my_scenes.json --output my_video.mp4
  python veo_extension.py scenes.json --verbose

Scene JSON Format:
  {
    "scenes": [
      {
        "prompt": "Scene 1 description",
        "params": {"aspect_ratio": "16:9", "resolution": "720p"}
      },
      {
        "prompt": "Scene 2 description",
        "params": {"aspect_ratio": "16:9"}
      }
    ]
  }
        """
    )
    
    parser.add_argument('scenes_file', help='Path to JSON file containing scene definitions')
    parser.add_argument('-o', '--output', help='Custom output filename')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        extender = VeoVideoExtension()
        
        logger.info("="*60)
        logger.info("VEO SCENE-BASED VIDEO EXTENSION")
        logger.info("="*60)
        
        video_path = extender.extend_from_scenes_file(
            scenes_file=args.scenes_file,
            output_filename=args.output
        )
        
        logger.info("="*60)
        logger.info(f"✓ SUCCESS! Extended video saved to: {video_path}")
        logger.info("="*60)
        return 0
        
    except Exception as e:
        logger.error("="*60)
        logger.error(f"✗ ERROR: {e}")
        logger.error("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
