try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
setup(name='embedc',
    version='0.21',
    py_modules=['embedc'],
    description='Python Embedded C',
    author='Fernando Trias',
    author_email='sub@trias.org',
    url='http://pyembedc.sourceforge.net'
    )
