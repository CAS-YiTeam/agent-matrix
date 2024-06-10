"""

rm -r dist
pip install .
python -m build
cp ./dist/*.whl ./release
cp ./dist/gradio-3.32.10-py3-none-any.whl /home/fuqingxu/faka-docker-compose/faka-docker-compose/gpt_academic/docs/gradio-3.32.10-py3-none-any.whl


"""

import setuptools, glob, os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def _process_requirements():
    packages = open('requirements.txt').read().strip().split('\n')
    requires = []
    for pkg in packages:
        if pkg.startswith('git+ssh'):
            return_code = os.system('pip install {}'.format(pkg))
            assert return_code == 0, 'error, status_code is: {}, exit!'.format(return_code)
        else:
            requires.append(pkg)
    return requires

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('agent_matrix')


setuptools.setup(
    name="agent_matrix",
    version="4.0.0",
    author="QingxuFu",
    author_email="qingxu.fu@outlook.com",
    description="Generating high-level intelligent agents via nesting basic LM agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/binary-husky/agent-matrix/",
    project_urls={
        "Bug Tracker": "https://github.com/binary-husky/agent-matrix/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    package_data={"": extra_files},
    include_package_data=True,
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.8",
    install_requires=_process_requirements(),
)