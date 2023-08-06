from setuptools import setup


setup(
    name='paraturegmailfeed',
    version='0.10',
    description='ETL for Parature emails routed to Gmail account',
    url='https://github.com/joelcolucci/paraturegmailfeed',
    author='Joel Colucci',
    author_email='joelcolucci@gmail.com',
    license='MIT',
    packages=['paraturegmailfeed','paraturegmailfeed.gmailhandler', 'paraturegmailfeed.paratureaction'],
    install_requires=[
        'google-api-python-client',
        'pymongo'
    ],
    zip_safe=False
)
