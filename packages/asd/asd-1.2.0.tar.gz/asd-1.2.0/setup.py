from setuptools import setup, find_packages

setup(
    name = "asd",
    description = "Various command line helper scripts`",
    version = "1.2.0",
    author = 'Lajos Santa',
    author_email = 'santa.lajos@coldline.hu',
    url = 'https://github.com/voidpp/asd.git',
    install_requires = [
        "argcomplete==1.0.0",
        "voidpp-tools>=1.1.1",
    ],
    scripts = [
        'bin/asd',
    ],
    include_package_data = True,
    packages = find_packages(),
)
