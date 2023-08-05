from setuptools import setup

setup(
    name='quanthub',
    version='0.1',
    py_modules=['main'],
    install_requires=[
        'Click',
        's3cmd',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        quanthub=main:cli
    ''',
)
