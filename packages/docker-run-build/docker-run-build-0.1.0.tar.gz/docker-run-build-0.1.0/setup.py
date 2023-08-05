from setuptools import setup, find_packages


VERSION = '0.1.0'


setup(
    name='docker-run-build',
    version=VERSION,
    description="Incrementally build Docker images",
    author="Caio Ariede",
    author_email="caio.ariede@gmail.com",
    url="http://github.com/caioariede/docker-run-build",
    license="MIT",
    zip_safe=False,
    platforms=["any"],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['docker-run-build=docker_rb.cli:main'],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ],
    include_package_data=True,
    install_requires=[
        'six',
        'docker-py==1.6.0',
        'click==6.2',
    ],
)
