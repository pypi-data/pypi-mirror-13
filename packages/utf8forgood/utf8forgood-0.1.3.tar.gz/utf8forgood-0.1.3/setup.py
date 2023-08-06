from setuptools import setup, find_packages
setup(
    name="utf8forgood",
    version="0.1.3",
    include_package_data=True,
    zip_safe=False,
    author='miraculixx',
    author_email='miraculixx at github',
    description='"Simple is better than complex", Tim Peters, The Zen Of Python',
    long_description=open('README.md').read(),
    license='BSD',
    packages=find_packages(),
    )
