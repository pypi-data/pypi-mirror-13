from setuptools import setup

setup(
    name='RAPIDpy',
    version='2.0.1',
    description='Python scripting interface for the RAPID progam. More information about installation and the input parameters can be found at http://rapid-hub.org. The source code for RAPID is located at https://github.com/c-h-david/rapid/.',
    keywords='RAPID',
    author='Alan Dee Snow',
    author_email='alan.d.snow@usace.army.mil',
    url='https://github.com/erdc-cm/RAPIDpy',
    download_url='https://github.com/erdc-cm/RAPIDpy/tarballs/2.0.1',
    license='MIT',
    packages=['RAPIDpy'],
    install_requires=['python-dateutil', 'netCDF4', 'numpy', 'pytz', 'requests'],
)
