from setuptools import setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as reqs:
    requirements = reqs.read().split("\n")

setup(
    name="PeerFinder",
    version="2020.07.24",
    packages=["peerfinder"],
    url="https://github.com/rucarrol/PeerFinder",
    license="BSD 3-Clause",
    author="Ruairi Carroll",
    author_email="ruairi.carroll@gmail.com",
    description="A tool to find common IX points as per PeeringDB",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    entry_points={"console_scripts": ["peerfinder=peerfinder.peerfinder:main"],},
)
