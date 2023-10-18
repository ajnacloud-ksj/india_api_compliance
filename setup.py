from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in india_api_compliance/__init__.py
from india_api_compliance import __version__ as version

setup(
	name="india_api_compliance",
	version=version,
	description="API QR Code solution for India compliance",
	author="Ajna Cloud",
	author_email="paramesh@ajna.cloud",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
