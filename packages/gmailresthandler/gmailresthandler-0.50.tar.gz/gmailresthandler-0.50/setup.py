from setuptools import setup


setup(
    name='gmailresthandler',
    version='0.50',
    description='Helper classes for working with Gmail API client.',
    url='https://github.com/joelcolucci/gmailresthandler',
    author='Joel Colucci',
    author_email='joelcolucci@gmail.com',
    license='MIT',
    packages=['gmailresthandler'],
    install_requires=[
        'google-api-python-client'
    ],
    zip_safe=False
)
