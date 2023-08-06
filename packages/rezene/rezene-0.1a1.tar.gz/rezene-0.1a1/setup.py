from setuptools import setup, find_packages


setup(
    name='rezene',
    version='0.1a1',
    description='An alternative API for lxml',
    url='https://github.com/propars/rezene',
    author='Cengiz Kaygusuz',
    author_email='cengiz@propars.net',
    classifiers=[
        'Development Status :: 3 - Alpha'
    ],
    packages=find_packages(),
    keywords='lxml xml data',
    install_requires=['lxml']
)
