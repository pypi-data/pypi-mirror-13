from setuptools import setup, find_packages

setup(
    name='sockpuppet',
    version='0.1.0',
    author='Chris Withers',
    author_email='chris@withers.org',
    license='MIT',
    description="Tools for integration tests involving real ports",
    # long_description=open('docs/description.rst').read(),
    url='http://sockpuppet.readthedocs.org',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(),
    include_package_data=True,
    extras_require=dict(
        test=['nose', 'nose-cov', 'nose-fixes',
              'testfixtures', 'mock', 'coveralls', 'manuel'],
        build=['sphinx', 'pkginfo', 'setuptools-git']
    )
)
