from setuptools import setup
from zoom.__version__ import __version__

setup(
    name='zoom',
    packages=['zoom'],
    version=__version__,
    description='Distributed project management',
    author='Sunny Sagar',
    author_email='trexinabluecape@gmail.com',
    url='https://github.com/ssagar0/zoom',
    install_requires=['click', 'pyaml'],
    entry_points={
        'console_scripts': [
            'zoom=zoom:entrypoint',
        ],
    },
    license='MIT',
    keywords='git repo',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Version Control'
    ],
)
