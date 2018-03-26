from distutils.core import setup

setup(
    name='hillie',
    version='1.0',
    description='A tool to query and manipulate okular and pdf annotations',
    long_description=open('README.md').read(),
    author='Matthias Baumgartner',
    author_email='dev@igsor.net',
    url='https://github.com/igsor/hillie/',
    packages=['hillie'],
    package_data = {
        '': ['README.md'],
        'hillie': ['data/collected-words', 'data/stems.t', 'data/words.t']
        },
    scripts = ['anedit', 'hillie-p', 'hillie-o', 'pusher'],
    license='Free for use',
    requires=('lxml', 'stemming', 'levenshtein', 're', 'urllib', 'poppler', 'glib', 'magic', 'sqlite3')
)

## EOF ##
