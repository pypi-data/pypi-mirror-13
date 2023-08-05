# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='stacks-image',
    packages=find_packages(),
    version='0.2.1',
    author=u'Jonathan Ellenberger',
    author_email='jonathan_ellenberger@wgbh.org',
    url='http://stacks.wgbhdigital.org/',
    license='MIT License, see LICENSE',
    description=(
        "A Stacks application for handling images and lists of images."
    ),
    long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=[
        'django-versatileimagefield>=1.2.2',
        'django-textplusstuff>=0.5',
        'stacks-page>=0.1.1'
    ],
    package_data={
        'stacks_image': [
            'static/sass/*.scss',
            'static/js/*.js',
            'static/js/vendor/lazyimages/*.js',
            'static/js/vendor/owl/*.js',
            'templates/stacks_image/stacksimage/*.html',
            'templates/stacks_image/stacksimagelist/*.html'
        ]
    },
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ]
)
