#!/usr/bin/env python

import shutil
import glob
import os

from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.install import install


class CustomInstallCommand(install):
    def run(self):
        install.run(self)

        service_file = Path(__file__).parent / "pcreporter.service"
        user_systemd_dir = Path("/etc/systemd/user/")

        shutil.copy(service_file, user_systemd_dir / "pcreporter.service")
        print(f"Installed systemd service to {user_systemd_dir / 'pcreporter.service'}")

        # Optionally reload systemd user daemon

        print("To enable the service, run:")
        print("systemctl --user daemon-reload")
        print("systemctl --user enable pcreporter.service")
        print("systemctl --user start pcreporter.service")


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


install_requires = read("requirements.txt").splitlines()

# Dynamically determine extra dependencies
extras_require = {}
extra_req_files = glob.glob("requirements-*.txt")
for extra_req_file in extra_req_files:
    name = os.path.splitext(extra_req_file)[0].replace("requirements-", "", 1)
    extras_require[name] = read(extra_req_file).splitlines()

if extras_require:
    extras_require["all"] = sorted({x for v in extras_require.values() for x in v})


meta = {}
exec(read("pcreporter/__meta__.py"), meta)


# Handle turning a README file into long_description
long_description = meta["description"]
readme_fname = ""
long_description = read("README.md")
long_description_content_type = "text/markdown"

setup(
    # Essential details on the package and its dependencies
    name=meta["name"],
    version=meta["version"],
    # packages=["pcreporter", "pcreporter.info", "pcreporter.monitor", "pcreporter.fn"],
    packages=find_packages(),
    # package_dir={meta["name"]: os.path.join(".", meta["path"])},
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    # Metadata to display on PyPI
    author=meta["author"],
    author_email=meta["author_email"],
    description=meta["description"],
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    license=meta["license"],
    url=meta["url"],
    cmdclass={"install": CustomInstallCommand},
    entry_points={
        "console_scripts": [
            "pc_reporter=pcreporter.cli:main",
        ],
    },
)
