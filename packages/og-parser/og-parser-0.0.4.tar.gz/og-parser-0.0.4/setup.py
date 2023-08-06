from distutils.core import setup
setup(
        name    = 'og-parser',
        version = '0.0.4',
        py_modules = ['ogParser'],
        author = 'Daewook Shin',
        author_email = 'daeuky1@gmail.com',
        url = 'https://github.com/singun/og-parser',
        description = 'A simple OPEN GRAPH parser',
        install_requires = ['flask', 'beautifulsoup4']
        )

