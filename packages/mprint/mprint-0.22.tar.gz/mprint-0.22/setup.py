from setuptools import setup

setup(
        name="mprint",
        version="0.22",
        description="Use tags to print markup text on console screen",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: Microsoft",
            "Operating System :: POSIX",
            "Operating System :: Unix",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: User Interfaces",
            "Topic :: Terminals"
            ],
        keywords="print tags color markup",
        url="http://www.github.com/h0m3/python-mprint",
        author="Artur 'h0m3' Paiva",
        author_email="dr.hoome@gmail.com",
        license="MIT",
        packages=["mprint"],
        install_requires=[
                "colorama"
        ],
        include_package_data=True,
        zip_safe=False
    )
