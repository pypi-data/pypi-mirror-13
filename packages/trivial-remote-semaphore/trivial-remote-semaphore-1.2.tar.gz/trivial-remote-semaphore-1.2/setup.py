from setuptools import setup
setup(
    name='trivial-remote-semaphore',
    version='1.2',

    description="Trivial Remote Semaphore (client & server)",
    url="https://bitbucket.org/gclinch/trivial-remote-semaphore",
    license='Apache License, Version 2.0',

    author='Graham Clinch',
    author_email='g.clinch@lancaster.ac.uk',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: System :: Distributed Computing'],

    packages=['trivial_remote_semaphore'],
    install_requires=['pyzmq'],
    entry_points={'console_scripts': [
        'trs-client=trivial_remote_semaphore.client:run',
        'trs-server=trivial_remote_semaphore.server:run'
        ]})
