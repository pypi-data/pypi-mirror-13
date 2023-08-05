from setuptools import find_packages, setup


setup(
    name='django-croco',
    packages=find_packages(),
    include_package_data=True,
    version='1.0.0',
    description='',
    long_description=open('README.rst').read(),
    author='Incuna & @mlen108',
    url='https://github.com/incuna/django-croco/',
    install_requires=[
        'crocodoc',
    ],
    zip_safe=False,
)
