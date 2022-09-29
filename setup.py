'''
Created on Jan 18, 2019

@author: mboscolo
'''

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="OdooQtUi",
    version="0.0.3",
    author="Daniel Smerghetto",
    author_email="daniel.smerghetto@omniasolutions.eu",
    description="The project intend to get a fully qt ui version for odoo, providing form a search view to be used in non web environment, like Allocation extension.",
    long_description=long_description,
    include_package_data=True,
    install_requires=['PySide2'],
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/mboscolo/odoo_qt/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
)
