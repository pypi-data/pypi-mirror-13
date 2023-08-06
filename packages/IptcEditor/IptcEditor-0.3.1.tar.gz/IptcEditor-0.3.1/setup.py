from setuptools import setup, find_packages

###################################################################

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Topic :: Utilities",
]

INSTALL_REQUIRES = ['gi', 'datetime']

###################################################################
# # BOILER PLATE CODE


setup(
    name="IptcEditor",
    description="This is a python3 GTK3 wrapper for the EXIV2 application, which is used to read and edit IPTC (and other forms) of image metadata. " \
                "It can handle bulk operations on directories of image files.",
    license="GNU General Public License v3 or later (GPLv3+)",
    url="https://www.zaziork.com",
    version=open('VERSION.rst').read(),
    author="Dan Bright",
    author_email="productions@zaziork.com",
    maintainer="Dan Bright",
    maintainer_email="productions@zaziork.com",
    keywords=["ITPC", "image metadata editor", "ITPC metadata editor"],
    long_description=open('README.rst').read(),
    packages=find_packages() + ['IptcEditor/resources'],
    package_dir={"IptcEditor": "IptcEditor"},
    zip_safe=False,
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    include_package_data=True
)
