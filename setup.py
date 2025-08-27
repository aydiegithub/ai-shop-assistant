from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="AI Shop Assist",       
    version="1.0.0",
    author="Aditya Dinesh K",
    author_email="developer@aydie.in",
    description="AI Shop Assistant Project",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),   
    package_dir={"": "src"},               
    python_requires=">=3.9",               
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)