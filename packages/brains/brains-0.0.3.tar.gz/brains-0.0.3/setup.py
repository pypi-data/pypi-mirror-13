from setuptools import setup


try:
    with open('README.md') as readme:
        long_description = readme.read()
except (IOError, ImportError):
    long_description = ''

entry_points = {
    'console_scripts': [
        'brains = brains:cli',
    ]
}

setup(
    install_requires=[
        "click==6.2",
        "pyyaml==3.11",
        "termcolor==1.1.0",
        "requests==2.9.0",
    ],
    name="brains",
    py_modules=["brains"],
    entry_points=entry_points,
    version="0.0.3",
    author="Eric Carmichael",
    author_email="eric@ckcollab.com",
    description="Helps submit files to brains app",
    long_description=long_description,
    license="MIT",
    url="https://github.com/dev-coop/brains-cli",
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
