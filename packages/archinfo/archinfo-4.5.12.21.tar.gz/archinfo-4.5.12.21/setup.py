from distutils.core import setup
setup(
    name='archinfo',
    version='4.5.12.21',
    packages=['archinfo'],
    install_requires=[ 'capstone', 'pyelftools' ]
)
