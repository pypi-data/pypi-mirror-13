from setuptools import setup

with open("version.txt") as f:
    ver = f.read().strip()

with open("README.rst") as f:
    long_description = f.read()

setup(
    name='hessianfree',
    packages=['hessianfree'],
    version=ver,
    description='Hessian-free optimization for deep networks',
    long_description=long_description,
    author='Daniel Rasmussen',
    author_email='drasmussen@princeton.edu',
    url='https://github.com/drasmuss/hessianfree',
    download_url='https://github.com/drasmuss/hessianfree/tarball/%s' % ver,
    keywords=['neural network', 'hessian free', 'deep learning'],
    license="BSD",
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Scientific/Engineering'],
)
