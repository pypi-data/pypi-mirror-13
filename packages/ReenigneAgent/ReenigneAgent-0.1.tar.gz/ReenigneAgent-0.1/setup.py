try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
        'description': 'Reenigne Monitoring Agent',
        'author': 'Matt Vandermeulen, Reenigne',
        'url': 'https://monitor.reenigne.net',
        'version': '0.1',
        'install_requires': [ 'requests' ],
        'packages': [
            'ragent',
            'ragent.modules',
            'ragent.utils',
        ],
        'scripts': [ ],
        'name': 'ReenigneAgent',
        'entry_points': {
            'console_scripts': [
                'reenigne-monitoring-agent = ragent.agent:main'
            ],
        },
}

setup(**config)
