from setuptools import setup, find_packages
 
setup(
    name='deploy_utils',
    version='0.3.0',
    description='Utilities for deploying projects to EC2',
    url='https://github.com/evansiroky/deploy_utils',
    author='Evan Siroky',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],
    keywords='AWS Fabric deployment',
    packages=find_packages(),
    install_requires=[
        'boto>=2.38',
        'fabric>=1.10.1',
        'django-fab-deploy>=0.7.5'
    ],
    entry_points={
        'console_scripts': [
            'launch_amazon_linux=deploy_utils.example_script:amazon_linux_test_battery',
            'launch_centos6=deploy_utils.example_script:centos6_test_battery'
        ]
    },
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True
)
