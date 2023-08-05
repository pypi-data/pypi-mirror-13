from setuptools import setup

setup(
    name='odkmodel',
    version="0.1.2",
    description='SQLAlchemy models for the auto-generated schema by ODKAggregate',
    author='Jeffrey Meyers',
    author_email='jeffrey.alan.meyers@gmail.com',
    license='MIT',
    packages=['odkmodel'],
    install_requires=[
        "SQLAlchemy==1.0.11"
    ],
    zip_safe=False
)
