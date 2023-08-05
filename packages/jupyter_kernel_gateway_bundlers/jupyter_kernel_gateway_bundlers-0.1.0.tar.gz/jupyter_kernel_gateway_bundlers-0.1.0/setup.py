# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop

from notebook.services.config import ConfigManager

# Get location of this file at runtime
HERE = os.path.abspath(os.path.dirname(__file__))

# Eval the version tuple and string from the source
VERSION_NS = {}
with open(os.path.join(HERE, 'kernel_gateway_bundlers/_version.py')) as f:
    exec(f.read(), {}, VERSION_NS)

def _install_notebook_extension():
    cm = ConfigManager()
    print('Installing notebook extension')
    cm.update('notebook', { 
        'jupyter_cms_bundlers': {
            'microservice_dockerfile_download': {
                'label': 'Microservice Docker bundle (.zip)',
                'module_name': 'kernel_gateway_bundlers.dockerfile_download',
                'group': 'download'
            }
        }
    })

class InstallCommand(install):
    def run(self):
        super(InstallCommand, self).run()
        _install_notebook_extension()

class DevelopCommand(develop):
    def run(self):
        super(DevelopCommand, self).run()
        _install_notebook_extension()

setup(
    name='jupyter_kernel_gateway_bundlers',
    author='Jupyter Development Team',
    author_email='jupyter@googlegroups.com',
    description='Plugins for jupyter_cms to deploy and download notebooks as kernel gateway microservices',
    long_description = '''
    This package adds a *Download as* menu item that packages the current notebook, 
a Dockerfile, and a README in a zip download. When built, the Docker image is
configured to expose the notebook as a HTTP microservice using the 
jupyter_kernel_gateway.

See `the project README <https://github.com/jupyter-incubator/kernel_gateway_bundlers>`_
for more information. 
''',   
    url='https://github.com/jupyter-incubator/kernel_gateway_bundlers',
    version=VERSION_NS['__version__'],
    license='BSD',
    platforms=['Jupyter Notebook 4.0.x'],
    packages=[
        'kernel_gateway_bundlers'
    ],
    install_requires=['jupyter_cms>=0.3.0'],
    cmdclass={
        'install': InstallCommand,
        'develop': DevelopCommand,
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ]
)