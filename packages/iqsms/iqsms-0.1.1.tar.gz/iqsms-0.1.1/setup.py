try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


setup(
    name='iqsms',
    version='0.1.1',
    packages=['iqsms'],
    zip_safe=False,
    include_package_data=True,
    author='Kirill Zhuravlev',
    author_email='kazhuravlev@fastmail.com',
    url='https://github.com/kazhuravlev/iqsms',
    description='IQsms.ru client',
    license='The MIT License (MIT)',
    install_requires=['six==1.10.0'],
)
