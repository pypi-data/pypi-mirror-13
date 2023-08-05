from distutils.core import setup

setup(
    name='DBUSSimpleNotify',
    version='0.2.3',
    author='Egil Hasting',
    author_email='eh@higen.org',
    packages=['dbussimplenotify'],
    scripts=['dbussimplenotify/dbussimplenotify.py'],
    url='http://pypi.python.org/pypi/DBUSSimpleNotify/',
    license='MIT',
    description='Dead simple notify class for DBUS.',
    long_description=open('README.txt').read(),
    platforms = ['linux'],
    classifiers = [
           'Development Status :: 3 - Alpha',
           
    # Pick your license as you wish (should match "license" above)
     'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    ],

)
