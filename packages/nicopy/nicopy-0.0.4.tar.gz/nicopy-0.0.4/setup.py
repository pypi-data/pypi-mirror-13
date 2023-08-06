from setuptools import setup, find_packages
from os import path
import markdown

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description_md = f.read()
md = markdown.Markdown()
long_description = md.convert(long_description_md)

setup(
    name='nicopy',
    version = '0.0.4',
    description='niconico api for python',
    long_description=long_description,
    url = 'http://github.com/roronya/nicopy',
    author='roronya',
    author_email='roronya628@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='niconico api',
    packages=find_packages(exclude=['tests*']),
    install_requires=['requests', 'lxml', 'beautifulsoup4'],
)
