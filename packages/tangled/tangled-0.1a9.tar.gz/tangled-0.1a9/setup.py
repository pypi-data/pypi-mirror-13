from setuptools import setup, PEP420PackageFinder


setup(
    name='tangled',
    version='0.1a9',
    description='Tangled namespace and utilities',
    long_description=open('README.rst').read(),
    url='http://tangledframework.org/',
    download_url='https://github.com/TangledWeb/tangled/tags',
    author='Wyatt Baldwin',
    author_email='self@wyattbaldwin.com',
    packages=PEP420PackageFinder.find(include=['tangled*']),
    extras_require={
        'dev': (
            'coverage>=3.7.1',
            'nose>=1.3.3',
            'pep8>=1.5.7',
            'pyflakes>=0.8.1',
            'Sphinx>=1.2.2',
            'sphinx_rtd_theme>=0.1.6',
        )
    },
    entry_points="""
    [console_scripts]
    tangled = tangled.__main__:main

    [tangled.scripts]
    release = tangled.scripts:ReleaseCommand
    scaffold = tangled.scripts:ScaffoldCommand
    python = tangled.scripts:ShellCommand
    test = tangled.scripts:TestCommand

    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
