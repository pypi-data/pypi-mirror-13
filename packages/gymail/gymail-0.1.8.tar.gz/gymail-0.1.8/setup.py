from distutils.core import setup
from setuptools import find_packages

setup(
    name="gymail",
    version="0.1.8",
    author="eayin2",
    author_email="eayin2 at gmail dot com",
    packages=find_packages(),
    url="https://github.com/eayin2/gymail",
    description="gymail wraps around smptlib and MIMEMultipart to send either warning, error or info mails to a recipient, \
                 using html and css to markup and format the email appropriately, thus gymail can be used to send email notifications from scripts.",
    entry_points={
        'console_scripts': [
            'gymail = gymail.core:argparse_entrypoint',
        ],
    },
    install_requires=[],
)
