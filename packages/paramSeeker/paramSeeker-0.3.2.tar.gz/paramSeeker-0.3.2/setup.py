# coding=utf8
from setuptools import setup
__author__ = 'hellflame'


setup(
    name='paramSeeker',
    version="0.3.2",
    keywords=('param', 'parameter', 'terminal handler'),
    description="Terminal parameter retrive then 执行以及参数转发，开发实体内容",
    license='Apache License',
    author='hellflame',
    author_email='hellflamedly@gmail.com',
    url="https://github.com/hellflame/paramSeeker",
    packages=[
        'paramSeeker'
    ],
    platforms="any",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        "Operating System :: OS Independent"
    ],
    entry_points={
        'console_scripts': [
            'seeker=paramSeeker.example:test_env'
        ]
    }
)


