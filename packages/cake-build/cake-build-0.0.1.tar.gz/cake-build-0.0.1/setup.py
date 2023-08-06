"""
ya ya, setup cake and stuffs
"""

from setuptools import setup

setup(
  name="cake-build",
  version="0.0.1",
  description="metabuild for c/c++",
  url="https://github.com/mylhne/cake",
  author="Myles Hathcock",
  author_email="myles@mylhne.sh",
  license="MIT",
  py_modules=["cake"],
  entry_points = {
    "console_scripts" : ["cake=cake:main"]
  }
)

