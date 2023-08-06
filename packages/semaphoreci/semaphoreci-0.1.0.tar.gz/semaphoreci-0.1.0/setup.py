import setuptools

import semaphoreci

packages = setuptools.find_packages(exclude=[
    'tests',
    'tests.integration',
    'tests.unit'
])
requires = [
    'requests'
]

setuptools.setup(
    name="semaphoreci",
    version=semaphoreci.__version__,
    description="Python wrapper for the Semaphore CI API",
    long_description="\n\n".join([open("README.rst").read(),
                                  open("LATEST_VERSION_NOTES.rst").read()]),
    license='Apache-2.0',
    author="Ian Cordasco",
    author_email="graffatcolmingov@gmail.com",
    url="https://semaphoreci.readthedocs.org",
    packages=packages,
    install_requires=requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
