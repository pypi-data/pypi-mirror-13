# N.B. to push a new version to PyPi, update the version number
# in rfhub/version.py and then run 'python setup.py sdist upload'
from setuptools import setup

execfile('rfhub/version.py')

setup(
    name             = 'gprfhub',
    version          = __version__,
    license          = 'Apache License 2.0',
    zip_safe         = False,
    include_package_data = True,
    install_requires = ['Flask', 'watchdog', 'robotframework', 'tornado'],
    packages         =[
        'rfhub',
        'rfhub.blueprints',
        'rfhub.blueprints.api',
        'rfhub.blueprints.doc',
        'rfhub.blueprints.dashboard',
        ],
    scripts          =[], 
)
