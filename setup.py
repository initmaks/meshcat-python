import sys
from setuptools import setup, find_packages

setup(name="meshcat",
    version="0.4.0",
    description="WebGL-based visualizer for 3D geometries and scenes",
    url="https://github.com/initmaks/meshcat-python",
    download_url="https://github.com/initmaks/meshcat-python/archive/v0.4.0.tar.gz",
    author="Maks Sorokin",
    author_email="mksmsrkn@gmail.com",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    test_suite="meshcat",
    entry_points={
        "console_scripts": [
            "meshcat-server=meshcat.servers.zmqserver:main"
        ]
    },
    install_requires=[
      "ipython >= 8.35.0",
      "u-msgpack-python >= 2.8.0",
      "numpy >= 2.2.4", 
      "tornado >= 6.4.2",
      "pyzmq >= 26.4.0",
      "pyngrok >= 7.2.3",
      "pillow >= 11.2.1"
    ],
    zip_safe=False,
    include_package_data=True
)
