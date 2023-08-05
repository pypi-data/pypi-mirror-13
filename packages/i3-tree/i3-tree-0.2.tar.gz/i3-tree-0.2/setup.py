from setuptools import setup

setup(
    name="i3-tree",
    version="0.2",
    author="Pierre Wacrenier",
    author_email="mota@souitom.org",
    description="Convenient Python lib to manipulate an i3 WM tree",
    url="http://github.com/mota/i3-tree",
    license="ISC",
    install_requires=["i3-py==0.6.4"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    packages=["i3_tree"],
)
