from setuptools import setup, find_packages


setup(
    name='stock',
    version='0.1',
    author='Hiroyuki Ishii',
    py_modules=['pystock'],
    packages=find_packages(),
    description='A command line tool for stock markets',
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        pystock=pystock.cmd:cli
    ''',
    )
