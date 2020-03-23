import setuptools
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='aiohttp_asynctools',
    version='0.1.3',
    description='Some function and classes to help you deal with aiohttp sessions',
    url='https://github.com/cglacet/aiohttp-sessions-helpers',
    project_urls={
        'Bug Reports': 'https://github.com/cglacet/aiohttp-sessions-helpers/issues',
        'Source': 'https://github.com/cglacet/aiohttp-sessions-helpers/',
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Christian Glacet',
    author_email='cglacet@kune.tech',
    license='MIT',
    zip_safe=False,
    install_requires=[
        "aiohttp >= 3.3"
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=[
        "pytest",
        "pytest-asyncio",
    ],
    extras_require={
        "example": [
            "aiohttp_jinja2 >= 1.1.1",
        ]
    },
    packages=setuptools.find_packages(exclude=("tests",)),
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)