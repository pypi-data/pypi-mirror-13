from setuptools import setup

setup(name='shufflecrypt',
	classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security :: Cryptography',
      ],
        version='0.12',
        description='ShuffleCrypt rearranges the pixels in a image with help of a key. -help for help',
        url='',
	author='Ivar Matstoms',
        author_email='ivar.matstoms@gmail.com',
        license='GPL',
        scripts=['bin/shufflecrypt'],
        zip_safe=False)
