from setuptools import setup

setup(
    name='tprofile',
    version='0.0.15',
    packages=['tprofile'],
    author='timchow',
    author_email='jordan23nbastar@yeah.net',
    license='LGPL',
    install_requires=["tornado>=3.1.1"],
    description="a profile tool for tornado web requesthandler",
    keywords='tornado profile',
    url='http://timd.cn/',
    entry_points={
        "console_scripts":[
            "test_tprofile_server=tprofile.test_server:main",
        ],
    },
    package_data={
        'tprofile': ['usage.txt'],
    },
    long_description=open("tprofile/usage.txt").read()
)

