from setuptools import setup, find_packages

setup(
    name='pyElizaChatbotClient',
    version='0.1.6',
    author="Luis Fernando D'Haro",
    author_email='luisdhe@i2r.a-star.edu.sg',
    license='LICENSE.txt',
    packages=find_packages(exclude=['contrib', 'docs',]),
    include_package_data = True,
    package_data={'test': 'test/pyElizaChatbotClient.py'},
    url='http://workshop.colips.org/re-wochat/',
    description='Basic stand-alone/websocket client for using in the Re-WoChat Shared task.',
    long_description=open('README.txt').read(),
    keywords='chatbots eliza re-wochat shared-task',
    install_requires=[
        "nltk >= 3.1",
        "petl >= 1.1.0",
        "future >= 0.15.2",
        "twisted >= 15.5.0",
        "autobahn[twisted] >= 0.11.0",
    ],
)

