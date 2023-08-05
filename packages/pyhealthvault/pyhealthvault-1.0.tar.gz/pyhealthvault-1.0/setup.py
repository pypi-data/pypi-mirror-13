from setuptools import setup, find_packages

setup(
    name='pyhealthvault',
    version='1.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    author='Rajeev S',
    author_email='rajeevs1992@gmail.com',
    maintainer='Rajeev S',
    maintainer_email='rajeevs1992@gmail.com',
    description='Python SDK for HealthVault',
    license='MIT',
    url='https://github.com/rajeevs1992/pyhealthvault',
    download_url='https://github.com/rajeevs1992/pyhealthvault/archive/master.zip',
    install_requires=[
        'cryptography==1.1',
        'enum34==1.0.4',
        'lxml==3.5.0',
        'pycrypto==2.6.1',
        'python-dateutil==2.4.2',
        'pytz==2015.6',
        ],
    )
