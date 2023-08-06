from setuptools import setup, find_packages


setup(
    name='keybin-client',
    version='0.1',
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        "requests==2.9.1",
    ],
    description="Keybin client library",
    author="MarcDufresne",
    author_email="marc.andre.dufresne@gmail.com",
    url="https://github.com/MarcDufresne/keybin-client",
)