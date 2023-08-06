from setuptools import setup, find_packages

with open('requirements.txt') as req_file:
    requirements = [r.strip() for r in req_file.readlines()]

with open('test_requirements.txt') as test_req_file:
    test_requirements = [r.strip() for r in test_req_file.readlines()]

setup(
    name='textlocal',
    packages=find_packages(),
    install_requires=requirements,
    tests_require=test_requirements,
    test_suite='textlocal.test',
    version='0.1.0',
    author='James Fenwick',
    author_email='j.fenwick@me.com'
)
