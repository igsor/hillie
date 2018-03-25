from distutils.core import setup

pkg = ['hillie']

pkg_data = {
    'hillie': ['anedit', 'collected-words', 'gpop', 'hillie', 'hillie-o', 'pusher', 'stems.t', 'words.t']
    }


setup(
    name='hillie',
    version='1.0',
    description='A tool to query and manipulate okular and pdf annotations',
    long_description=open('README.md').read(),
    author='Matthias Baumgartner',
    author_email='dev@igsor.net',
    url='http://www.igsor.net/projects/hillie/',
    packages=pkg,
    package_data = pkg_data,
    scripts = ['anedit', 'gpop', 'hillie', 'hillie-o', 'pusher'],
    license='Free for use',
    requires=('lxml', 'stemming', 'levenshtein', 're', 'urllib', 'poppler', 'glib', 'magic', 'sqlite3')
)

## EOF ##
