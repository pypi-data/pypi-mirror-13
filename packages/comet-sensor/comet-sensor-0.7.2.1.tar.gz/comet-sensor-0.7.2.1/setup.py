from setuptools import setup, find_packages
from pip.req import parse_requirements


install_reqs = parse_requirements("./requirements.txt")
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='comet-sensor',
    version='0.7.2.1',
    author = "Rovanion Luckey",
    author_email = "rovanion.luckey@gmail.com",
    description = ("A simple tool for retreiving and dealing with climate data from the Comet T6540 Climate sensor."),
    license = "GPL3",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "examples"]),
    entry_points='''
        [console_scripts]
        comet-sensor=comet.main:cli
    ''',
    include_package_data = True,
    install_requires=reqs
)
