from distutils.core import setup

setup(
    name='DBUSSimpleNotify',
    author='Egil Hasting',
    version="0.2.4",
    author_email='eh@higen.org',
    packages=['dbussimplenotify'],
    scripts=['dbussimplenotify/dbussimplenotify.py'],
    url='https://github.com/ehasting/DBUSSimpleNotify',
    download_url='https://github.com/ehasting/DBUSSimpleNotify',
    keywords="DBUS notify",
    license='MIT',
    description='Dead simple notify class for DBUS.',
    long_description=open('README.txt').read(),
    platforms=['linux'],
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 ],

)
