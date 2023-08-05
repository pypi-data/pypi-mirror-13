from setuptools import find_packages, setup

setup(
    name='about_py',
    version='0.0.3',
    author=u'Cees van Wieringen',
    author_email='ceesvw@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['GitPython==1.0.1',],
    url='https://github.com/ceasaro/about_py',
    license='',
    description=open('DESCRIPTION').read(),
    long_description=open('README.md').read(),
    zip_safe=False,
)