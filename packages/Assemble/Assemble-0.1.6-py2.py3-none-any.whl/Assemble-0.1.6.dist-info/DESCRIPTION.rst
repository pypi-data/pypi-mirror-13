Assemble: Assemble the packages!
=============================================

.. teaser-begin

``Assemble`` is an `MIT <http://choosealicense.com/licenses/mit/>`_-licensed Python package that allows you to
simplify package building.

A quick example::

    # file: setup.py
    from assemble import get_package

    package = get_package()

    keywords = [
        "about", "this", "package"
    ]
    classifiers = [
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",

        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",

        "Topic :: Software Development :: Libraries :: Python Modules",
    ]

    if __name__ == "__main__":
        package.setup(keywords, classifiers)

The package also offers a nice and easy cli interface to test, build and publish your package::

    assemble test
    assemble patch-version
    assemble build
    assemble upload --environment test


