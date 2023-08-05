from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), "infi", "dtypes", "iqn", "__version__.py")) as version_file:
    exec(version_file.read()) # pylint: disable=W0122

setup(name="infi.dtypes.iqn",
      classifiers=[
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
      ],
      description="Datatype for IQN",
      license="PSF",
      author="Dror Levin",
      author_email="drorl@infinidat.com",
      url="https://github.com/infinidat/infi.dtypes.iqn",
      version=__version__, # pylint: disable=E0602
      packages=find_packages(exclude=["tests"]),
      namespace_packages=["infi", "infi.dtypes"],
      zip_safe=False,
)
