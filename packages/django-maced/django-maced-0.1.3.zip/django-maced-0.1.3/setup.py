from setuptools import setup, find_packages

setup(
    name='django-maced',
    version='0.1.3',
    # find_packages() takes a source directory and two lists of package name patterns to exclude and include.
    # If omitted, the source directory defaults to the same directory as the setup script.
    packages=find_packages(),
    url='https://github.com/Macainian/Django-Maced',
    license='MIT License',
    author='Keith Hostetler',
    author_email='khostetl@nd.edu',
    description='Django app designed to help with easy database record manipulation/creation. It is called Maced for Merge Add Clone Edit Delete.',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)