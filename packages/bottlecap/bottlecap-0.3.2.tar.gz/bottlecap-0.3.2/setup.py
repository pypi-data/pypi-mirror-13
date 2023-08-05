from setuptools import setup, find_packages
setup(
    name="bottlecap",
    description="Extras for Bottle",
    author='Cal Leeming',
    author_email='cal@iops.io',
    url='https://github.com/foxx/bottlecap',
    keywords=['bottle', 'bottlecap', 'helpful'],
    version="0.3.2",
    py_modules=['bottlecap', 'helpful'],
    setup_requires=[
        'pytest-runner>=2.6',
        'yanc>=0.3'
    ],
    install_requires=[
        'bottle',
        'click',
        'werkzeug',
        'six'
    ],
    tests_require=[
        'bottle>=0.12',
        'pytest-benchmark>=3.0',
        'pytest-raisesregexp>=2.1',
        'pytest-cov>=2.2',
        'pytest>=2.8',
        'webtest>=2.0',
        'python-coveralls',
        'tox',
        'six'
    ],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4'
    ]
)