#!/usr/bin/env python
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

setup(
    name='mdx_picture',
    version='0.1.2',
    author='Artem Grebenkin',
    author_email='speechkey@gmail.com',
    description='Python-Markdown extension supports the <picture> tag.',
    url='https://github.com/speechkey/mdx_picture',
    download_url='https://github.com/speechkey/mdx_picture/tarball/0.1.2',
    packages=['mdx_picture', 'mdx_picture.tests'],
    install_requires=['Markdown>=2.0'],
    license="MIT License",
    platforms=['any'],
    keywords=['markdown', 'picture'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
    test_suite='mdx_picture.tests.get_suite'
)
