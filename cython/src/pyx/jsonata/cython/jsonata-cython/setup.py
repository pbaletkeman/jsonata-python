from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
import pathlib
import sys

# Python 3.11+ has tomllib built-in, older versions need tomli
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib

# Read version from pyproject.toml
with open("pyproject.toml", "rb") as f:
    pyproject_data = tomllib.load(f)
    version = pyproject_data["project"]["version"]

# Path to the source directory
SRC_DIR = pathlib.Path("src/jsonata_cython")

# Collect all .pyx files
pyx_files = list(SRC_DIR.glob("*.pyx"))

extensions = [
    Extension(
        f"jsonata_cython.{pyx.stem}",  # Module name
        [str(pyx)],                    # Source file
    )
    for pyx in pyx_files
]

setup(
    name="jsonata-cython",
    version=version,  # ✅ synced from pyproject.toml
    author="Your Name",
    author_email="you@example.com",
    description="A Cython-accelerated implementation of JSONata",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Cython",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
