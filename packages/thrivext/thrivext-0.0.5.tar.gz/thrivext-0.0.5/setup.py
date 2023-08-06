from distutils.core import setup

setup(
    name = "thrivext",
    packages = ["thrivext"],
    package_data = {"thrivext": ["templates/*"]},
    include_package_data=True,
    version = "0.0.5",
    install_requires = [
        "jinja2",
        "arrow"
    ],
    description = "Thrive client extensions",
    author = "Rohan Kekatpure",
    author_email = "rohan_kekatpure@intuit.com",
    url = "https://github.com/rohan-kekatpure/thrivext",
    download_url = "https://github.com/rohan-kekatpure/thrivext/tarball/0.1",
    keywords = ["pypi", "Thrive"],
    classifiers = []
)