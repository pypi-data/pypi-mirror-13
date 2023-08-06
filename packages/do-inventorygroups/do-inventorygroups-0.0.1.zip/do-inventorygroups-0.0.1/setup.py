from setuptools import setup

setup(
    name="do-inventorygroups",
    version='0.0.1',
    scripts=['doinventorygroups.py'],
    author='Coastal',
    author_email='liam@co.astal.io',
    url='https://github.com/coastalio/do-inventorygroups',
    install_requires=[
        'requests',
        'six',
        'wheel',
        'dopy'
    ]
)