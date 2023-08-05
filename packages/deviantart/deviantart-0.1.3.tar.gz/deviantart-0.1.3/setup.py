from setuptools import setup

setup(
    name="deviantart",
    version="0.1.3",
    description="A Python wrapper for the DeviantArt API",
    url='https://github.com/neighbordog',
    author="Kevin Eichhorn",
    author_email="kevineichhorn@me.com",
    license='MIT',
    packages=["deviantart"],
    install_requires=[
        "sanction"
    ]
)