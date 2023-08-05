from setuptools import setup, find_packages

setup(
    name='lrn_click',
    packages=find_packages(),
    version='0.1.5',
    description='Helper Click library to provide enhanced prompts',
    author='Alan Garfield',
    author_email='alan.garfield@learnosity.com',
    url='https://github.com/Learnosity/lrn_click',
    download_url='https://github.com/Learnosity/lrn_click/tarball/0.1.5',
    keywords=[],
    classifiers=[],
    include_package_data=True,
    install_requires=[
        'click',
        'boto3',
        'iptools'
    ],
)
