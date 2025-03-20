from typing import List
from setuptools import setup, find_packages

def get_requirements(file_path:str)->List[str]:
    requirements = []
    with open(file_path, 'r') as file:
        requirements = file.readlines()
        requirements = [req.replace("\n","") for req in requirements]
        if "-e ." in requirements:
            requirements.remove("-e .")
    return requirements
    
setup(
    name='document_format_verifier',
    version='0.1',
    author='Dipesh Ghimire',
    author_email='dipeshghimire.dg@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)