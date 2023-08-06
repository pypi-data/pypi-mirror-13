import subprocess
from setuptools import setup, find_packages


def get_long_description():
    cmd = 'pandoc -f markdown_github -t rst README.md --no-wrap'
    try:
        return subprocess.check_output(cmd, shell=True, universal_newlines=True)
    except:
        return ""

VERSION = '1.1.0'

setup(
    name='relatime',
    version=VERSION,
    author='Steve McMaster',
    author_email='mcmaster@hurricanelabs.com',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    url='https://github.com/mcm/relatime',
    description='Python parser for a simple relative time syntax',
    long_description=get_long_description(),
    install_requires=["pytz", "python-dateutil"],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Development Status :: 4 - Beta',
    ],
    bugtrack_url='https://github.com/mcm/relatime/issues',
)
