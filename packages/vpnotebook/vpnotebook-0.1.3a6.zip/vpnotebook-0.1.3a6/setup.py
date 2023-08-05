from distutils.core import setup
from os.path import join

try:
    from vpnotebook import cmdclass
except:
    import pip, importlib
    pip.main(['install', 'vpnotebook']); cmdclass = importlib.import_module('vpnotebook').cmdclass

setup(
    name='vpnotebook',
    packages=['vpnotebook'],
    version='0.1.3a6',
    description='pip installable VPython kernel for Jupyter Notebook',
    long_description=open('README.txt').read(),
    author='John Coady, Bruce Sherwood, Ruth Chabay',
    author_email='johncoady@shaw.ca',
    url='http://pypi.python.org/pypi/vpnotebook/',
    license='New BSD License',
    keywords='vpython kernel',
    classifiers=[
          'Framework :: IPython',
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Natural Language :: English',
          'Programming Language :: Python',
    ],
    cmdclass=cmdclass(join('vpnotebook','data')),
    package_data={'vpnotebook': ['data/kernel.json']},
    
)
