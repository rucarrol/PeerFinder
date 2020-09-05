from setuptools import setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as reqs:
    requirements = reqs.read().split("\n")

setup(
    name="peerfinder",
    version="2020.09.05",
    packages=["peerfinder"],
    url="https://github.com/rucarrol/PeerFinder",
    license="MIT",
    author="Ruairi Carroll",
    author_email="ruairi.carroll@gmail.com",
    description="A tool to find common IX points on PeeringDB",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    entry_points={"console_scripts": ["peerfinder=peerfinder.peerfinder:main"],},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
