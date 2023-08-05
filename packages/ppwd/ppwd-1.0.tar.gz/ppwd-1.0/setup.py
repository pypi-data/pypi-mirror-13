from setuptools import setup, find_packages

PACKAGE = "ppwd"
NAME = "ppwd"
DESCRIPTION = "Private Password Manager"
AUTHOR = "Youchao Feng"
AUTHOR_EMAIL = "fengyouchao@gmail.com"
URL = "https://github.com/fengyouchao/ppm"
VERSION = __import__(PACKAGE).__version__

setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        # long_description=read("README.md"),
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        license="Apache License, Version 2.0",
        url=URL,
        packages=find_packages(),
	install_requires = ['prettytable>=0.7.2',
	    "pycrypto>=2.6.1",
	    ],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
        ],
        entry_points={
            'console_scripts': [
                'ppm = ppwd.ppm:main',
            ]
        },
        zip_safe=False,
)
