#!/usr/bin/env python

from distutils.core import setup

setup(
      name='django-template-iminifier',
      version='1.1',
      description='Python package, providing simple django template loader. It reduces HTML output in templates by stripping out whitespace characters between HTML and django template tags. Originally forked from  iRynek',
      author='Ahmad Dukhan',
      author_email='cpadmin@gmail.com',
      url='https://github.com/bhappyz/django-template-iminifier',
      download_url='https://github.com/bhappyz/django-template-iminifier/archive/master.zip',
      license='MIT',
      keywords=['django', 'template', 'minify'],  # arbitrary keywords
      packages=[
          'template_minifier',
          'template_minifier.template',
          'template_minifier.template.loaders',
      ],
      requires=[
          'Django',
      ],
)
