from setuptools import setup

setup(
    name="subtitlematcher",
    version="0.0.4",
    description="Matching videos and subtitles file names",
    long_description=open('README.rst', 'r').read(),
    url="http://github.com/itsjef/subtitlematcher.git",
    author="Duc Anh Tran",
    author_email="td.anh0812@gmail.com",
    license='MIT',
    packages=['subtitlematcher'],
    install_requires=['future'],
    entry_points={
        'console_scripts': ['subtitlematcher=subtitlematcher.__main__:main']
    },
    zip_safe=False
)
