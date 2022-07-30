import setuptools


setuptools.setup(
    name='check_dayz_server',
    version='0.1.0',
    description='Check DayZ server player count.',
    packages=['check_dayz_server'],
    install_requires=[
        'requests==2.28.1',
        'python-dotenv==0.20.0'
    ],
    entry_points={
        'console_scripts': [(
            'check_dayz_server='
            'check_dayz_server.__main__:main'
        )]
    }
)
