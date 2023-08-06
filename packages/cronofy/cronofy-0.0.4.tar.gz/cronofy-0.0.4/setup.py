from distutils.core import setup

setup(
    name='cronofy',
    version='0.0.4',
    author='Derek Edwards',
    author_email='derek.edwards@coachlogix.com',
    packages=['cronofy', 'cronofy.test'],
    url='http://www.coachlogix.com',
    license='MIT',
    description='Cronofy Python SDK',
    long_description='README.md',
    install_requires=[
        "requests >= 2.5.3"
    ],
)
