#!/usr/bin/env python
# -*- coding:utf-8 -*-

# to make the plugin package for auto-upgrades:
# ./setup.py sdist

import os
import sys
import json
from setuptools import setup, Command


with open("plugin.json") as defsin:
    defs = json.load(defsin)

defs.update({
    "description": "Domain Name Server for Phen",
    "url": "https://phen.eu",
    "packages": ["phen.plugins.dns"],
    "package_dir": {"phen.plugins.dns": "."},
    "package_data": {"phen.plugins.dns": ["plugin.json"]},
    "classifiers": [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: Name Service (DNS)',
        'Framework :: Twisted',
        'License :: OSI Approved :: '
        'GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 2',
        # Twisted Names still does not support Python 3 for dns servers
        # 'Programming Language :: Python :: 3',
    ],
})


if "sdist" in sys.argv:
    idx = sys.argv.index("sdist")
    sys.argv.insert(idx + 1, "--formats")
    sys.argv.insert(idx + 2, "zip")
    # with open("README") as longdesc:
    #     defs["long_description"] = longdesc.read()


class BumpVersion(Command):
    description = "update and tag the new version wherever needed"
    user_options = [
        ("set-version=", "V", "new version (default: increase revision)"),
        ("yes", "y", "non-interactive, i.e. answer yes to all questions"),
    ]
    boolean_options = ["yes"]

    def initialize_options(self):
        self.set_version = None
        self.yes = False

    def finalize_options(self):
        if self.set_version is None:
            tver = defs["version"].split(".")
            tver[-1] = str(int(tver[-1]) + 1)
            self.set_version = ".".join(tver)

    def run(self):
        defs["version"] = self.set_version
        new_defs = json.dumps(defs, sort_keys=True, indent=1)
        if not self.yes:
            print(new_defs)
            raw_input("Ctrl+C now to interrupt, Enter to write changes...")
        with open("plugin.json", "wt") as defsout:
            defsout.write(new_defs)
        os.system("git add plugin.json")
        os.system('git commit -m "version {}"'.format(self.set_version))
        os.system(
            'git tag -s -m "release of version {0}" v{0}'
            .format(self.set_version)
        )


defs["packages"] = [s.encode("utf8") for s in defs["packages"]]

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

st_defs = defs.copy()
# this plugin is under the umbrela of the phen project
# so we should add the namespace
st_defs["name"] = "phen." + st_defs["name"]
st_defs["long_description"] = long_description
st_defs["cmdclass"] = {
    "bump_version": BumpVersion,
}

setup(**st_defs)
