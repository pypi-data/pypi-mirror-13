from setuptools import setup

# create README file
with open('src/manual.rst') as f:
    manual = f.read()
with open('INSTALL.rst') as f:
    install = f.read()
with open('README.rst', 'w') as f:
    install = f.write('\n\n'.join([manual, install]))

setup(
    name='sshdeploy',
    version='1.1.0',
    description="Generates and distributes SSH keys.",
    author="Ken Kundert",
    author_email='sshdeploy@nurdletech.com',
    url='http://nurdletech.com/linux-utilities/sshdeploy',
    download_url='https://github.com/kenkundert/sshdeploy/tarball/master',
    entry_points = {
        'console_scripts': [
            'sshdeploy=src.main:main',
        ],
    },
    zip_safe = False,
    packages=['src'],
    package_data={'src': ['manual.rst']},
    license='GPLv3+',
    install_requires=[
        'arrow',
        'docopt',
        'inform',
        'pexpect',
        'shlib',
        #'abraxas', -- not yet in pypi
    ],
    keywords=[
        'ssh',
        'keys',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ],
)
# vim: set sw=4 sts=4 et:
