# Sample https://github.com/pypa/sampleproject

from setuptools import setup

setup(
    name='serviceslib',
    version='1.0.0',
    packages=['services_lib'],
    url='https://github.com/drmobile/services-lib',
    license='',
    author='Soocii',
    author_email='service@soocii.me',
    description='Library for Soocii back-end services which include common functions/scripts/libraries.',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.5',
    ],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['click', 'Fabric3', 'boto3', 'awscli']
)
