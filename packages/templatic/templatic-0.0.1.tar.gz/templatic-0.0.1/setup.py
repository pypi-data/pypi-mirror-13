from distutils.core import setup

requires = ['jinja2>=2.8',
            'pyyaml>=3.11']

setup(
    name='templatic',
    version='0.0.1',
    packages=[''],
    url='https://github.com/romankonz/templatic',
    license='',
    author='Roman Konz',
    author_email='roman@konz.me',
    description='',
    scripts=['bin/templatic'],
    install_requires=requires,
)
