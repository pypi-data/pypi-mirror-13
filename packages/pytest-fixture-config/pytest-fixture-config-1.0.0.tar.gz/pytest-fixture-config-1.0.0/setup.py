import os
from setuptools import setup

execfile(os.path.join(os.path.pardir, 'common_setup.py'))

classifiers = [
    'License :: OSI Approved :: MIT License',
    'Development Status :: 5 - Production/Stable',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Testing',
    'Topic :: Utilities',
    'Intended Audience :: Developers',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
]

install_requires = ['pytest']

tests_require = ['pytest-cov',
                 'six',
                 ]

if __name__ == '__main__':
    kwargs = common_setup('pytest_fixture_config')
    kwargs.update(dict(
        name='pytest-fixture-config',
        description='Fixture configuration utils for py.test',
        author='Edward Easton',
        author_email='eeaston@gmail.com',
        classifiers=classifiers,
        install_requires=install_requires,
        tests_require=tests_require,
        py_modules=['pytest_fixture_config'],
    ))
    setup(**kwargs)
