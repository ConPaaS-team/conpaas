from setuptools import setup, find_packages

console_scripts = [
    'conpaasdb-controller = conpaasdb.controller.cmd:main',
    'conpaasdb-manager = conpaasdb.manager.server:main',
    'conpaasdb-agent = conpaasdb.agent.server:main'
]

setup(
    name='conpaasdb',
    version='1.0',
    description='ConPaaS DB layer',
    author='Contrail',
    author_email='email@example.com',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    classifiers=['Operating System :: POSIX :: Linux',
                 'Programming Language :: Python'],
    zip_safe=False,
    entry_points={
        'console_scripts': console_scripts,
    })
