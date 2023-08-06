from setuptools import setup
import os
import re


def get_changelog():
    here = os.path.abspath(".")
    text = open(os.path.join(here, 'CHANGELOG')).read()
    header_matches = list(re.finditer('^-+$', text, re.MULTILINE))
    # until fifth header
    text = text[:header_matches[5].start()]
    # all lines without fifth release number
    lines = text.splitlines()[:-1]
    return "Changelog\n=========\n\n" + "\n".join(lines)


README = open(os.path.abspath('README.rst')).read()
CHANGELOG = get_changelog()


setup(
    name="devpi-web",
    description="devpi-web: a web view for devpi-server",
    long_description="\n\n".join([README, CHANGELOG]),
    url="http://doc.devpi.net",
    version='2.6.0',
    maintainer="Holger Krekel, Florian Schulze",
    maintainer_email="holger@merlinux.eu",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"] + [
            "Programming Language :: Python :: %s" % x
            for x in "2.7 3.3".split()],
    entry_points={
        'devpi_server': [
            "devpi-web = devpi_web.main"]},
    install_requires=[
        'Whoosh',
        'beautifulsoup4>=4.3.2',
        'defusedxml',
        'devpi-server>=2.6.0.dev0,<3dev',
        'devpi-common>=2.0.5.dev0',
        'docutils>=0.11',
        'pygments>=1.6',
        'pyramid',
        'pyramid-chameleon'],
    include_package_data=True,
    zip_safe=False,
    packages=['devpi_web', 'devpi_web.vendor'])
