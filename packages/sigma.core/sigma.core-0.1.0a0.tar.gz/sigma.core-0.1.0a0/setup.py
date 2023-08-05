from setuptools import setup


setup(
    name="sigma.core",
    version="0.1.0a0",
    packages=["sigma", "sigma.core"],
    namespace_packages=["sigma"],
    install_requires=[],
    extras_require={},
    zip_safe=True,
    package_data={
        "": ["*.txt", "*.rst", "*.md"]
    },
    author="Suzuki Shunsuke",
    author_email="suzuki.shunsuke.1989@gmail.com",
    description="Validation Library.",
    license="MIT",
    keywords="validation",
    url="https://github.com/pysigma/core",
)
