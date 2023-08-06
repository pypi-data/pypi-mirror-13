from setuptools import setup

setup(
    name='ncvx',
    version='0.1',
    author='Steven Diamond, Reza Takapoui, Stephen Boyd',
    packages=['ncvx'],
    license='GPLv3',
    zip_safe=False,
    install_requires=["cvxpy >= 3.5", "munkres"],
    use_2to3=True,
    url='http://github.com/cvxgrp/ncvx/',
    description='A CVXPY extension for problems with convex objective and decision variables from a nonconvex set.',

)
