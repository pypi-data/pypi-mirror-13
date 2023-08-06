from setuptools import setup, find_packages

setup(
    name='hybrid',
    version='1.1.3',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires = [
        "protobuf==3.0.0b2",
        "tornado>=3.1.1",
        "flask",
    ],
    entry_points={
        "console_scripts": [
            "hybrid = hybrid.commands:main",
        ],
    },

    author='timchow',
    author_email='jordan23nbastar@yeah.net',
    url='http://timd.cn/',
    description='hybrid tools set',
    keywords='hybrid server',
    license='LGPL',
)
