from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='k8s_autobuilder',
    version='0.0.1',
    description='A kubernetes-native CI/CD tool',
    long_description=long_description,
    license='MIT',
    url='https://github.com/HubbeKing/k8s_autobuilder',
    author='HubbeKing',
    author_email='github@hubbe.club',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools"
    ],
    project_urls={
        "Bug Tracker": "https://github.com/HubbeKing/k8s_autobuilder/issues"
    },
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        "Flask~=2.0.1",
        "kubernetes~=18.20.0",
        "gunicorn~=20.1.0",
        "jq~=1.2.1",
        "PyYAML~=5.4.1",
        "Werkzeug~=2.0.1"
    ]
)
