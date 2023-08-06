
from setuptools import setup

setup(name="Cyanide-And-Happiness",
      version="1.4",
      description="Automatically sets the latest Cyanide and Happiness comic as your background",
      url="https://github.com/sacert/Cyanide-And-Happiness",
      author="Stephen Kang",
      author_email="stephenkang9@gmail.com",
      packages=["cynhap"],
      install_requires=[
      'beautifulsoup4',
      'pillow',
      'requests'
      ],
      scripts=["src/cynhap"]
)
