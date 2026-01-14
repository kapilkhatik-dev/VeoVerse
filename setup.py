"""
Setup script for Veo v3 Video Generation Library
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read version from config
version = "1.0.0"

setup(
    name="veo-video-generator",
    version=version,
    author="Veo Video Generator Team",
    author_email="",
    description="A Python library for generating AI-created videos using Google's Veo v3 model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/veo-video-generator",
    packages=find_packages(exclude=["tests", "examples", "*.tests", "*.tests.*"]),
    py_modules=[
        "config",
        "utils",
        "veo_generator",
        "veo_extension",
        "model_discovery",
        "quick_start"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "google-genai>=0.3.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "image": ["Pillow>=10.0.0"],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "veo-generate=veo_generator:main",
            "veo-extend=veo_extension:main",
            "veo-models=model_discovery:main",
            "veo-cli=quick_start:main",
        ],
    },
    include_package_data=True,
    keywords="video generation ai veo google gemini artificial-intelligence",
    project_urls={
        "Documentation": "https://github.com/yourusername/veo-video-generator/blob/main/USAGE.md",
        "Source": "https://github.com/yourusername/veo-video-generator",
        "Bug Reports": "https://github.com/yourusername/veo-video-generator/issues",
    },
)
