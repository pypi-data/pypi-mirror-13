from distutils.core import setup

setup(
    name='tspfb',
    version='0.0.1',
    url="https://github.com/boundary/football-data-feed",
    author='David Gwartney',
    author_email='david_gwartney@bmc.com',
    packages=['tspfb', ],
#    entry_points={
#        'console_scripts': [
#            'actionhandler = boundary.webhook_handler:main',
#        ],
#    },
#    scripts=[
#        'tsp-cli-env.sh',
#   ],
#    package_data={'boundary': ['templates/*']},
    license='Apache 2',
    description='NFL play by play data and tools for demonstrations within TrueSight Pulse',
    long_description=open('README.txt').read(),
    install_requires=[
        "tspapi >= 0.1.2",
    ],
)
