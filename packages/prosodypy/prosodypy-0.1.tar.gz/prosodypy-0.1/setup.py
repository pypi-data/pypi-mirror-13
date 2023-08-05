from distutils.core import setup

setup(
    name='prosodypy',
    description='A compatibility suite to write modules in Python for Prosody'
                'XMPP Server',
    author='Sergey Dobrov',
    author_email='binary@jrudevels.org',
    version='0.1',
    url='https://github.com/jbinary/prosodypy',
    packages=[
        'prosodypy',
        'prosodypy.examples',
        'prosodypy.mod_prosodypy',
        'prosodypy.twilix_compat',
    ],
)
