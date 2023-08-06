from distutils.core import setup

setup(
    name = "django_shark",
    packages = ["shark_core"],
    package_data = {"shark_core": ['templates/*.html', 'static/shark/css/*.css', 'static/shark/js/*.js', 'static/shark/fonts/*.eot', 'static/shark/fonts/*.svg', 'static/shark/fonts/*.ttf', 'static/shark/fonts/*.woff', 'static/shark/fonts/*.woff2']},
    version = "0.0.4",
    description = "Django based bootstrap web framework",
    author = "Bart Jellema",
    author_email = "b@rtje.net",
    url = "https://pypi.python.org/pypi/shark/0.0.4",
    install_requires=[
        'Markdown',
        'Django'
    ],
    keywords = ["django", "bootstrap", "framework"],
    classifiers = [
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