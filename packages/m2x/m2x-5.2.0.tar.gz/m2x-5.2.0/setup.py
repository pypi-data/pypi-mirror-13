from setuptools import setup


version = __import__('m2x').version

LONG_DESCRIPTION = """
AT&T's M2X is a cloud-based fully managed data storage service for network
connected machine-to-machine (M2M) devices. python-m2x is python client to M2X
API. API documentation at https://m2x.att.com/developer/documentation
"""

setup(
    name='m2x',
    version=version,
    author='Citrusbyte',
    author_email='matias.aguirre@citrusbyte.com',
    description='M2X Python API client',
    license='MIT',
    keywords='m2x, api',
    url='https://github.com/attm2x/m2x-python',
    packages=[
        'm2x',
        'm2x.v2',
        'm2x.tests',
        'm2x.tests.v2'
    ],
    long_description=LONG_DESCRIPTION,
    install_requires=[
        'requests>=2.0.1',
        'iso8601>=0.1.8',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3'
    ],
    test_suite='m2x.tests',
    zip_safe=False
)
