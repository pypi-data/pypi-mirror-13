try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'TodoApp',
    'description': 'Little todo script to keep track of things to do',
    'author': 'Eric Garza',
    'url': 'https://github.com/EricGarza/TodoApp',
    'download_url': 'https://github.com/EricGarza/TodoApp/archive/master.zip',
    'author_email': 'eric.garza13@gmail.com',
    'version': '0.1',
    'install_requires': ['prettytable'],
    'scripts': ['todo_app.py'],
}

setup(**config)
