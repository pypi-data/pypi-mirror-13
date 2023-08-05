#!/usr/bin/env python
#  coding=utf-8
# ---------------------------------------------------------------
# Desenvolvedor:    Arannã Sousa Santos
# Mês:              12
# Ano:              2015
# Projeto:          pagseguro_xml
# e-mail:           asousas@live.com
# ---------------------------------------------------------------

import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = u'API PagSegudo v2 e v3 em XML, baseado no projeto PYSPED'

setup(
    name='pagseguro_xml',
    version='0.0.4',
    description='API PagSeguro v2 e v3 em XML',
    long_description=readme,
    author='Aranna Sousa Santos',
    author_email='asousas@live.com',
    url='https://github.com/arannasousa/pagseguro_xml',
    download_url='https://github.com/arannasousa/pagseguro_xml/archive/master.zip',
    packages=find_packages(exclude=['exemplos', 'tests']),
    package_dir={'pagseguro_xml': 'pagseguro_xml'},
    install_requires=['requests', 'pytz', 'unidecode', 'lxml'],
    license='GNU General Public License v2 (GPLv2)',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: Portuguese (Brazilian)',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    keywords='pagseguro, payment, payments, credit-card, pagseguro_xml, xml, transacao, assinatura')