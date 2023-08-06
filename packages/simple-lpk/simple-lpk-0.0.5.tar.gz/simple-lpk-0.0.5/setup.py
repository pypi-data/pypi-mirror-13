from setuptools import setup

setup(
    name='simple-lpk',
    version='0.0.5',
    url='https://github.com/databasin/simple-lpk',
    license='see LICENSE',
    author='databasin',
    author_email='databasinadmin@consbio.org',
    description='Simple tool for creating an ArcGIS layer package from a shapefile',
    packages=['pkg'],
    include_package_data=True,
    install_requires=['click'],
    entry_points='''
        [console_scripts]
        pkg_lpk=pkg:pkg_lpk
    '''
)
