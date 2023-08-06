from distutils.core import setup

config = {
    'description': 'a dead simple name generator',
    'author': 'Ben Jones',
    'url': 'https://www.github.com/realsalmon/python-namesake/',
    'download_url': 'https://www.github.com/realsalmon/python-namesake/releases/tag/v0.1',
    'author_email': 'ben@fogbutter.com',
    'version': '0.1',
    'packages': ['namesake'],
    'name': 'namesake',
    'entry_points': {'console_scripts': ['namesake-name=namesake:main']},
    'package_data': {'namesake': ['data/nouns.txt',
                                  'data/verbs.txt',
                                  'data/adjectives.txt',
                                  'data/adverbs.txt']}
}

setup(**config)
