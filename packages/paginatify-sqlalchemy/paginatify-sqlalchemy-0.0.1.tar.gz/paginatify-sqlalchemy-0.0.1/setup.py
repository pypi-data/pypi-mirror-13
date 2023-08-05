from setuptools import setup

setup(
        name='paginatify-sqlalchemy',
        version='0.0.1',
        packages=['paginatify_sqlalchemy'],
        zip_safe=False,
        install_requires=['paginatify', 'sqlalchemy>=1.0.11']
)
