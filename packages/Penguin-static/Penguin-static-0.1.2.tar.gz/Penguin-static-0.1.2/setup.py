from setuptools import setup
import codecs


try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name == 'mbcs')
    codecs.register(func)


setup(
    # Application name:
    name="Penguin-static",

    # Version number:
    version="0.1.2",

    # Application author details
    author="Endi Sukaj",
    author_email="endisukaj@gmail.com",

    # Packages
    packages=["penguin"],
    include_package_data=True,
    package_data={'penguin': ['penguin/generator/*']},


    # Include additional files into the package

    description="Simple static site generator",

    entry_points={"console_scripts": [
        "penguin=penguin.main:main"
    ]},

    # Dependencies
    install_requires=[
        "argh",
        "Jinja2",
        "mistune",
        "pathtools",
        "py",
        "PyYAML",
        "watchdog",
    ],

)
