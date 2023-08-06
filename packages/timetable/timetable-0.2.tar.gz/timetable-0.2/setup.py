# encoding: utf-8
from setuptools import setup

setup(
    name='timetable',
    version='0.2',
    packages=['timetable', 'timetable.plot'],
    author='Ontje Lünsdorf',
    description='Generate timetables from iCal data.',
    long_description='\n'.join(
        open(f, 'rb').read().decode('utf-8')
        for f in ['README']),
    author_email='oluensdorf@gmail.com',
    url='https://bitbucket.org/luensdorf/timetable',
    keywords=['time', 'timetable', 'ical', 'calendar'],
    classifiers=[],
)
