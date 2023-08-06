from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='maguey',
    version='0.0.1',
    description='Python SDK for Agave API',
    long_description='Unofficial Python SDK for the Agave API',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Natural Language :: English',
    ],
    keywords='agave, hpc',
    url='http://github.com/andrewmagill/maguey',
    author='Andrew Magill',
    author_email='andrew.b.magill@gmail.com',
    license='MIT',
    packages=['maguey'],
    install_requires=[
        'markdown',
        'requests'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    zip_safe=False
)
