from setuptools import setup, find_packages

setup(
    name='cloud_lib',
    version='1.0.0',
    description='cloud service library',
    long_description='cloud service library',
    url='https://github.com/hoge',
    author='AkiraTaniguchi',
    author_email ='dededededaiou2003@yahoo.co.jp',
    packages=find_packages(),
    license = 'MIT',
    keywords='amazon google cloud bigquery storage s3 ec2',
    classifiers = [
      'Development Status :: 5 - Production/Stable',
      'Programming Language :: Python :: 2.7',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License'
    ],
    install_requires=['boto3==1.2.2', 'google-api-python-client==1.4.1', 'oauth2client==1.4.12']
)
