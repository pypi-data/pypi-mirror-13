from distutils.core import setup

setup(
    name='keep_iam_creds_fresh',
    version='0.1',
    packages=['keep_iam_creds_fresh'],
    url='',
    license='',
    author='dacc',
    author_email='dacc@uw.edu',
    description='Retrieve AWS temporary credentials, render configs from J2 templates and restart a service',
    entry_points={
        'console_scripts': [
            'keep_iam_creds_fresh = keep_iam_creds_fresh.main:main',
        ],
    },
)

