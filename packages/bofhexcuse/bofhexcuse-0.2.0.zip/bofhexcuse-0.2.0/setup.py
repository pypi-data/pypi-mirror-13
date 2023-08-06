from setuptools import setup

setup(
    name='bofhexcuse',
    version='0.2.0',
    packages=['bofhexcuse'],
    url='https://github.com/okzach/bofhexcuse/',
    license='',
    author='Zach Adams',
    author_email='zach@okzach.com',
    description='Generate random BOFH themed technical excuses!',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bofhexcuse=bofhexcuse:main'
        ]
    }
)
