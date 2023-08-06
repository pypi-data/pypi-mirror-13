#!/usr/bin/env python

from distutils.core import setup

setup(name='xml-models-redux',
      version='0.6.5',
      description='JSON/XML backed models queried from external REST apis',
      author='Chris Tarttelin and Cam McHugh',
      author_email='chris@pyruby.com',
      url='https://github.com/macropin/xml-models-redux',
      packages=['rest_client', 'xml_models', 'json_models','common_models'],
      install_requires=['mock', 'py-dom-xpath-redux']
     )
