from setuptools import setup, find_packages

setup(
    name="getawslogs",
    version="0.1.0",
    packages=find_packages(),
    description="Python package and non-interactive commandline program(s) to get AWS logs.",
    url="https://github.com/MelchiSalins/getawslogs",
    author="Melchi Salins",
    author_email="melchisalins@icloud.com",
    keywords='DevOps AWS Logs',
    install_requires=['boto3==1.2.1',
                      'botocore==1.3.2',
                      'simplejson',
                      'six'
                      ],
    scripts=['bin/get_vpc_logs']
)
