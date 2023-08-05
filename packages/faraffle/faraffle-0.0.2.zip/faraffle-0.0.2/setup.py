from setuptools import setup

setup(
    name='faraffle',
    version='0.0.2',
    packages=['faraffle'],
    url='https://github.com/Dreae',
    entry_points={
        "console_scripts": ['faraffle = faraffle.__main__:main']
    },
    license='MIT License',
    author='Dreae',
    author_email='penitenttangentt@gmail.com',
    description='Easy script for selecting FA raffle winners',
    install_requires=['requests', 'beautifulsoup4'],
    classifiers=[
        "Development Status :: 4 - Beta"
    ]
)
