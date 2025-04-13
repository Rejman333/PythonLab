from setuptools import setup

setup(
    name="pycluster",
    version="0.1",
    packages=["pycluster"],
    entry_points={
        'console_scripts': [
            'pycluster = pycluster.main:main'
        ]
    },
)