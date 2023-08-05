from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lambda-project-creator',

    version='0.0.7',

    description='lambda-project-creator project',
    long_description=long_description,

    url='https://github.com/cloudfish7/lambda-project-creator',

    author='cloudfish7',
    author_email='tskwdev@gmail.com',

    license='MIT',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='aws lambda lambda-uploader',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    package_data={
        'lambda_project_creator': ['template.json','template.txt'],
    },

    entry_points={
        'console_scripts': [
            'lambda-project-creator=lambda_project_creator.shell:main',
        ],
    },
)
