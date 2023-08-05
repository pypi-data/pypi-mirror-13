from setuptools import setup

setup(
    name='s2aiomulti',
    version='1.3',
    packages=['s2aios', 's2aior', 's2aiobe'],
    install_requires=['pymata-aio>=2.7',
                      'aiohttp>=0.19.0'],
    package_data={'s2aior': [('configuration/*'),
                            ('miscellaneous/*.txt'),
                            ('scratch_files/extensions/*.s2e'),
                            ('scratch_files/projects/*.sb2'),
                            ('Snap!Files/*.xml')]},


    entry_points={
        'console_scripts': [
            's2aios = s2aios.__main__:main',
            's2aior = s2aior.__main__:main',
            's2aiobe = s2aiobe.__main__:main'
        ]
    },
    url='https://github.com/MrYsLab/s2aiomulti/wiki',
    download_url='https://github.com/MrYsLab/s2aiomulti',
    license='GNU General Public License v3 (GPLv3)',
    author='Alan Yorinks',
    author_email='MisterYsLab@gmail.com',
    description='Arduino Multi-Board HTTP Controller and Router',
    keywords=['Firmata', 'Arduino', 'Scratch'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Topic :: Education',
    ],
)
