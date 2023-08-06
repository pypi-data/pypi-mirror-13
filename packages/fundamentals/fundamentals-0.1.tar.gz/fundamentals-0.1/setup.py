from setuptools import setup

version_num = __import__('fundamentals').__version__


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='fundamentals',
    version=version_num,
    description='Some project setup tools including logging, settings and database connections',
    long_description=readme(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    keywords=['logging', 'database'],
    url='https://github.com/thespacedoctor/fundamentals',
    download_url='https://github.com/thespacedoctor/fundamentals/archive/v%(version_num)s.zip' % locals(
    ),
    author='David Young',
    author_email='davidrobertyoung@gmail.com',
    license='MIT',
    packages=['fundamentals'],
    install_requires=[
        'pyyaml',
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3'],
    # entry_points={
    #     'console_scripts': ['fundamentals=fundamentals.cl_utils:main'],
    # },
    zip_safe=False
)
