from setuptools import setup, find_packages

with open("README.rst", "r") as f:
    long_description = f.read()

setup(
    name='v-run',
    version='0.0.2',
    author='Gustavo José de Sousa',
    author_email='gustavo.jo.sousa@gmail.com',
    description='Run commands using Python virtual environment',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/tualatrix/v-run',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    package_dir={'': 'src'},
    py_modules=['vrun'],
    install_requires=[
        'pexpect',
    ],
    python_requires='~=3.5',
    entry_points={
        'console_scripts': [
            'v-run = vrun:run',
        ]
    },
)
