#!/usr/bin/env python3
"""
Quick Start Script for Veo v3 Video Generation

This script provides a simple command-line interface to get started quickly.
"""
import sys
from pathlib import Path

def print_banner():
    print("\n" + "="*70)
    print("  VEO V3 VIDEO GENERATION - QUICK START")
    print("="*70 + "\n")

def print_menu():
    print("What would you like to do?\n")
    print("  1. Generate a single video from text")
    print("  2. Generate extended video from scenes (JSON file)")
    print("  3. List available models")
    print("  4. View examples")
    print("  5. Exit\n")

def generate_single_video():
    from veo_generator import VeoVideoGenerator
    
    print("\n--- Single Video Generation ---\n")
    prompt = input("Enter your video prompt: ").strip()
    
    if not prompt:
        print("Error: Prompt cannot be empty")
        return
    
    print("\nOptional parameters (press Enter to use defaults):")
    aspect_ratio = input("Aspect ratio (16:9, 9:16) [default: 16:9]: ").strip() or "16:9"
    resolution = input("Resolution (720p, 1080p) [default: 720p]: ").strip() or "720p"
    duration = input("Duration (4, 6, 8) [default: 8]: ").strip() or "8"
    
    try:
        duration = int(duration)
        
        print("\n" + "-"*70)
        print("Generating video... This may take several minutes.")
        print("-"*70 + "\n")
        
        generator = VeoVideoGenerator()
        video_path = generator.generate_video(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            duration_seconds=duration
        )
        
        print(f"\n✓ SUCCESS! Video generated at: {video_path}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")

def generate_from_scenes():
    from veo_extension import VeoVideoExtension
    
    print("\n--- Scene-Based Video Extension ---\n")
    scenes_file = input("Enter path to scenes JSON file [default: scenes.json]: ").strip()
    
    if not scenes_file:
        scenes_file = "scenes.json"
    
    if not Path(scenes_file).exists():
        print(f"Error: File not found: {scenes_file}")
        return
    
    try:
        print("\n" + "-"*70)
        print("Generating extended video... This may take several minutes per scene.")
        print("-"*70 + "\n")
        
        extender = VeoVideoExtension()
        video_path = extender.extend_from_scenes_file(scenes_file)
        
        print(f"\n✓ SUCCESS! Extended video generated at: {video_path}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")

def list_models():
    from model_discovery import print_all_models
    
    print("\n--- Available Models ---\n")
    print_all_models()
    
    input("Press Enter to continue...")

def view_examples():
    print("\n--- Example Scripts ---\n")
    print("Example scripts are located in the 'examples/' directory:\n")
    print("  1. simple_video_generation.py")
    print("     - Basic video generation with various parameters\n")
    print("  2. scene_based_extension.py")
    print("     - Multi-scene video creation and extension\n")
    print("  3. model_discovery_example.py")
    print("     - Discovering and listing available models\n")
    print("  4. image_to_video.py")
    print("     - Generate videos from images\n")
    print("Run them with: python examples/<script_name>.py\n")
    
    input("Press Enter to continue...")

def main():
    print_banner()
    
    # Check if API key is configured
    try:
        from config import GOOGLE_API_KEY
        if not GOOGLE_API_KEY:
            print("⚠ WARNING: GOOGLE_API_KEY not found in .env file")
            print("Please set your API key before generating videos.\n")
    except Exception as e:
        print(f"Error loading configuration: {e}\n")
        return
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            generate_single_video()
        elif choice == "2":
            generate_from_scenes()
        elif choice == "3":
            list_models()
        elif choice == "4":
            view_examples()
        elif choice == "5":
            print("\nGoodbye! 👋\n")
            break
        else:
            print("\nInvalid choice. Please enter 1-5.\n")
        
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye! 👋\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        sys.exit(1)
