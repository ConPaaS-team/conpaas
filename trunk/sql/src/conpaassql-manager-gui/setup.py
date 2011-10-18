from setuptools import setup, find_packages

console_scripts = [
    'conpaassql_manager_gui = ManagerGUI.server:main',
]

setup(
    name = 'conpaassql-manager-gui',
    version = '1.0.2',
    description = 'Simple GUI for ConPaaSSQL Manager',
    author = 'Luka Zakrajsek',
    author_email = 'luka.zakrajsek@xlab.si',
    package_dir = {'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    license = 'MIT',
    classifiers = ['License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python'],
    zip_safe = False,
    long_description = open('README.rst').read(),
    entry_points = {
        'console_scripts': console_scripts,
    },
    install_requires = [
        'Flask',
        'Flask-WTF',
        'conpaassql-server'
    ]
)
