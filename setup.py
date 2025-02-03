from setuptools import setup, find_packages

def read_requirements(filename):
    with open(filename, 'r') as f:
        return f.read().splitlines()

setup(
    name="AlphaChat", 
    version="0.1.0",
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
