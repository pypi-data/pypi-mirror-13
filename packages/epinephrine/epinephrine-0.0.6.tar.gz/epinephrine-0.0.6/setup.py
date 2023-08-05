from setuptools import setup, find_packages

appname = "epinephrine"

setup(
    name = appname,
    version = "0.0.6",
    packages = find_packages(),
    entry_points={
        'console_scripts': [
            '{appname} = {appname}.__main__:main'.format(appname=appname)
        ]
    },
    install_requires = [],
    author = "minamorl",
    author_email = "minamorl@minamorl.com",
)
