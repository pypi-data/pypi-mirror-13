from distutils.core import setup

setup(
    name = "django_shark",
    packages = ["shark_core"],
    version = "0.0.2",
    description = "Django based bootstrap web framework",
    author = "Bart Jellema",
    author_email = "b@rtje.net",
    url = "https://pypi.python.org/pypi/shark/0.0.2",
    install_requires=[
        'Markdown',
        'Django'
    ],
    keywords = ["django", "bootstrap", "framework"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = """\
Coming soon.
"""
)