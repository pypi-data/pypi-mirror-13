import runpy

from setuptools import setup

setup(
    name='earthpic',
    version=runpy.run_path('earthpic/__init__.py')['__version__'],
    packages=['earthpic', 'earthpic.tests'],
    url='https://github.com/pywkm/earthpic',
    license='BSD',
    author='Wiktor Matuszewski',
    author_email='pywkm@wukaem.pl',
    description='Earth photos downloader',
    long_description=(
        'Command line program to download Earth photos from\n'
        'http://himawari8.nict.go.jp website.'
    ),
    entry_points={
        'console_scripts': [
            'earthpic = earthpic.earth:main',
        ],
    },
    requires=['pytz', 'requests', 'Pillow', 'click'],
    platforms=['Windows'],
    classifiers=[
        'Topic :: Multimedia :: Graphics',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Win32 (MS Windows)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
