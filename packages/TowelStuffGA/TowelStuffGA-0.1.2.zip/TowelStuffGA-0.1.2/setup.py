from setuptools import setup

setup(
    name='TowelStuffGA',
    version='0.1.2',
    url='where to get it',
    author='R. Bergeron',
    author_email='rickboro@msn.com',
    
    packages=['towelstuff',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    entry_points={'console_scripts':['towscript=towelstuff.mycode:gtow',]}
)