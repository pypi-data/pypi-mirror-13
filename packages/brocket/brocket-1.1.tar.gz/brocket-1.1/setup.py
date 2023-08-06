from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='brocket',
    version='1.1',
    description='Build Amazon Associates Links in the clipboard super fast.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
        'Intended Audience :: End Users/Desktop',
        'Environment :: MacOS X',
    ],
    url='http://github.com/jachin/brocket',
    author='Jachin Rupe',
    author_email='jachin@jachin.rupe.name',
    license='MIT',
    packages=['brocket'],
    zip_safe=False,
    entry_points={
        'console_scripts': ['brocket=brocket.__main__:main'],
    },
    install_requires=[
        'urlobject',
        'pyperclip',
        'pync',
    ],
)
