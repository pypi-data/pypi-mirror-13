import nosehipchat.version
from setuptools import setup

setup(
    name="nose-hipchat",
    version=nosehipchat.version.__version__,
    author='Steve Leibman',
    author_email='sleibman@alum.mit.edu',
    description="Nose plugin to post test results to HipChat",
    license="MIT License",
    url="https://github.com/sleibman/nose-hipchat",
    packages=["nosehipchat"],
    install_requires=['nose'],
    classifiers=[
        "Topic :: Software Development :: Testing",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
    entry_points={
        'nose.plugins.0.10': [
            'nose-hipchat = nosehipchat.nosehipchat:NoseHipChat'
        ]
    }
)
