from distutils.core import setup

try:
    from jupyterpip import cmdclass
except:
    import pip, importlib
    pip.main(['install', 'jupyter-pip']); cmdclass = importlib.import_module('jupyterpip').cmdclass

setup(
    name='vpnotebook',
    version='0.1.01',
    description='pip installable VPython kernel for Jupyter Notebook',
    long_description=open('README.txt').read(),
    author='Bruce Sherwood, John Coady, Ruth Chabay',
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
    install_requires=['jupyter-pip'],
    packages=['vpnotebook'],
    cmdclass=cmdclass('vpnotebook/data'),
    package_data={'vpnotebook': ['data/kernel.json']},
    
)
