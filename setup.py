from setuptools import setup, find_packages

setup(
    name = "ipywe",
    version = "0.1",
    packages = find_packages(exclude=["tests"]),
    package_dir = {'': "."},
    test_suite = "tests",   
    install_requires = [
        "numpy",
        "ipywidgets",
        "traitlets",
        "scipy",
        "pillow",
    ],
    package_data = {
        '': ["*.js"],
    },
    dependency_links = [
    ],
    author = "ipywe team",
    description = "Widgets for iMars3D",
    license = 'BSD',
    keywords = [
        "neutron imaging",
        "ipywidgets",
        "jupyter widgets",
    ],
    url = "https://github.com/neutrons/ipywe",
)
