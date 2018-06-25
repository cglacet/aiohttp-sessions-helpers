import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='aiohttp_asynctools',
    version='0.0.2',
    description='Some function and classes to help you deal with aiohttp sessions',
    url='https://github.com/cglacet/aiohttp-sessions-helpers',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Christian Glacet',
    author_email='cglacet@kune.tech',
    license='MIT',
    zip_safe=False,
    install_requires=[
        "aiohttp >= 3.3.0"
    ],
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)