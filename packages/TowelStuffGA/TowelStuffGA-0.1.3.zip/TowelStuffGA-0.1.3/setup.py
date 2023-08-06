from setuptools import setup

setup(
    name='TowelStuffGA',
    version='0.1.3',
    url=' ',
    author='R. Bergeron',
    author_email='developer46@outlook.com',
    
    packages=['towelstuff',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    entry_points={'console_scripts':['towscript=towelstuff.my1',]}
)