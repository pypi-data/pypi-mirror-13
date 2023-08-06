import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))



setup(
    name='ebs_payment',
    version='0.8',
    description='This is a Django app for integrating with EBS payment SDK',
    url='https://bitbucket.org/redpandas/ebs_gateway_python',
    author_email='souranil@theredpandas.com',
    license='MIT License',
    packages=['ebs_gateway'],
    py_modules=['ebs'],
    zip_safe=False,
    include_package_data=True,
    long_description="README.rst",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
