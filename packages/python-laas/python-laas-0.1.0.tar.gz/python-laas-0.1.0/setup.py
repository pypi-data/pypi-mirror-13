"""
"""
from setuptools import setup

kw = {
    "name": "python-laas",
    "version": "0.1.0",
    "description": "Handy tools required to format your Python logs for LaaS/Splunk ingestion.",
    "long_description": __doc__,
    "url": "https://bitbucket.org/atlassianlabs/python-laas",
    "author": "Christopher Carter",
    "author_email": "chcarter@atlassian.com",
    "license": "MIT",
    "packages": [
        "laas",
    ],
    "install_requires": [
        "logstash_formatter",
    ],
    "zip_safe": False,
}

if __name__ == "__main__":
    setup(**kw)
