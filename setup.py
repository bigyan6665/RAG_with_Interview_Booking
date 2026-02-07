# setup.py is used to package the project as a reusable, installable Python module
from setuptools import find_packages, setup
from typing import List

HYPHEN_E_DOT = "-e ."


def get_requirements(file_path: str) -> List[str]:
    """
    This fn returns the list of requirements from requirements_dev.txt
    """
    requirements = []
    with open(file_path, encoding="utf-8-sig") as file:
        requirements = file.readlines()
        requirements = [req.replace("\n", "").strip() for req in requirements]
        if HYPHEN_E_DOT in requirements:
            requirements.remove(HYPHEN_E_DOT)
    return requirements


setup(
    name="booking chatbot",
    version="0.0.1",
    author="Bigyan Shrestha",
    author_email="bigyans04@gmail.com",
    packages=find_packages(),  # this fn will treat every folder that contain '__init__.py' file as a package. src and its subfolder in my case
    install_requires=get_requirements(
        "req.txt"
    ),  # includes the packages needed to be installed before using our ml app(custom package) package
)
