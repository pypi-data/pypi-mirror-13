from setuptools import setup, find_packages


setup(
    name='gateway-outage-responder',
    version='1.0.1',
    url='https://github.com/coddingtonbear/gateway-outage-responder',  # noqa
    description=(
        'If it looks like the internet is out; do something!'
    ),
    author='Adam Coddington',
    author_email='me@adamcoddington.net',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(),
    requirements=[
        'stanley-outlet-control',
    ],
    entry_points={
        'console_scripts': [
            'gateway-outage-responder = gateway_outage_responder.main:main'
        ],
    },
)
