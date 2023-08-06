try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


setup(
    name='lambdanow-python-client',
    version='0.1.2',
    url='http://www.lambdanow.com',
    license='Apache 2.0',
    author='LambdaNow',
    author_email='support@lambdanow.com',
    description='A Python client for LambdaNow clusters',
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development'
    ],
    platforms='any'
)

