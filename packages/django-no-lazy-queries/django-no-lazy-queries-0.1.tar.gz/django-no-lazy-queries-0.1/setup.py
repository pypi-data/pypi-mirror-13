from io import open

from setuptools import find_packages, setup

setup(
    name='django-no-lazy-queries',
    version='0.1',
    description='Prevent Django from automatically loading related models',
    long_description=open('README.rst', encoding='utf-8').read(),
    author='David Stensland',
    author_email='nolazyqueries@terite.com',
    url='https://github.com/terite/django-no-lazy-queries',
    download_url='https://pypi.python.org/pypi/django-no-lazy-queries',
    # license='BSD',
    packages=find_packages(exclude=('tests.*', 'tests')),
    install_requires=[
        'Django>=1.8',
        'contextlib2',
    ],
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        # 'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
