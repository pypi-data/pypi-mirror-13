import codecs
from setuptools import find_packages
from setuptools import setup


with codecs.open('README.rst', 'r', 'utf-8') as f:
    README = f.read()

with codecs.open('CHANGES.rst', 'r', 'utf-8') as f:
    CHANGES = f.read()

with codecs.open('CONTRIBUTORS.rst', 'r', 'utf-8') as f:
    CONTRIBUTORS = f.read()


requires = [
    'msgpack-python',
    'pyzmq',
]


setup(
    name='zmq_rpc',
    version='0.2',
    description='0mq RPC calls implemented with pyzmq.',
    long_description=u"{}\n{}\n{}".format(README, CONTRIBUTORS, CHANGES),
    classifiers=[
        'Programming Language :: Python',
    ],
    author='XCG Consulting',
    author_email='contact@xcg-consulting.fr',
    url='http://odoo.consulting',
    keywords='zmq rpc msgpack',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite='zmq_rpc',
)
