from setuptools import setup
setup(
    name="searchie-tools-yaml2json",
    description="Simple utility to transform yaml files to json format",
    version="0.0.5",
    maintainer="Eugene Krokhalev",
    maintainer_email = "rutsh@searchie.org",
    install_requires=[
        "pyyaml"
    ],
    py_modules=["yaml2json"],
    entry_points={
        "console_scripts": [
            "yaml2json = yaml2json:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Topic :: Software Development",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Utilities"
    ]
)
