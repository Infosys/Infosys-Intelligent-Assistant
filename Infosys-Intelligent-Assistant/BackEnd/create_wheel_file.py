__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import yaml
import subprocess
import os
with open(r'.\config\build_config.yaml') as build_file:
    build_config_list = yaml.safe_load(build_file)

with open('requirements.txt') as f:
    required = f.read().splitlines()

for build_config in build_config_list:

    try:
        print(build_config)

        if os.path.exists(f"./{build_config['packages']}"):

            setup_str = f"import setuptools\r" \
                        f"setuptools.setup(\r \
                name='{build_config['name']}',\r \
                version='{build_config['version']}',\r \
                author='{build_config['author']}',\r \
                author_email='{build_config['author_email']}',\r \
                description='{build_config['description']}',\r \
                long_description='{build_config['long_description']}',\r \
                classifiers={build_config['classifiers']},\r \
                package_dir={build_config['package_dir']},\r \
                packages=setuptools.find_packages(where='{build_config['packages']}'),\r \
                python_requires='{build_config['python_requires'][0]}',\r \
                install_requires={required})"

            with open('setup.py','w') as file:
                file.write(setup_str)

            subprocess.run(["python", "-m","build"])
            wheel_file = f"{build_config['name']}-{build_config['version']}-py3-none-any.whl"
            print(f"wheel_file: {wheel_file}")
            subprocess.run(["python", "-m", "pyc_wheel", f"dist\{wheel_file}"])
        else:
            print(f"Path does not exist ./{build_config['packages']}")
    except Exception as e:
        print(e)
