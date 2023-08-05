#!/usr/bin/env python
# recurring per-semester tasks in taskwarrior
# (c) 2016 Peadar Grant

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from tasklib.task import *
from datetime import datetime, timedelta
from dateutil import parser as dateparser
from argparse import ArgumentParser

def main():

    parser = ArgumentParser()
    parser.add_argument('--title', help='title stem string', required=True)
    parser.add_argument('--duedays', help='due on day 1=Monday-5=Friday comma separated')
    parser.add_argument('--project', help='project', default=None)
    parser.add_argument('--basedate', help='date of start week beginning (Monday)', required=True)
    parser.add_argument('--start', help='starting week number', default=4, type=int)
    parser.add_argument('--end', help='ending week number', default=13, type=int)
    parser.add_argument('--breakafterweek', help='mid term break after week', default=6, type=int)
    parser.add_argument('--breakforweeks', help='break length in weeks', default=1, type=int)
    parser.add_argument('--waitdays', help='hide tasks until x days before due', required=True, type=int)
    parser.add_argument('--dependprevious', help='depend on previous task', action='store_true')
    parser.add_argument('--save', help='save generated tasks', action='store_true', default=False)
    parser.add_argument('--dependson', help='task title to depend on (if exists)', default=None)
    options=vars(parser.parse_args())

    basedate = dateparser.parse(options['basedate'])
    start = options['start']
    end = options['end']
    breakafter = options['breakafterweek']
    breakweeks = options['breakforweeks']
    dependson = options['dependson']
    
    title = options['title']
    weekly = [int(e) for e in options['duedays'].split(',')]
    project = options['project']
    waitdays = options['waitdays']
    dependprevious = options['dependprevious']
    save = options['save']

    tw=TaskWarrior()    
    previous_task = None
    for week in range(start, end+1, 1):
        for period in range(1, len(weekly)+1, 1):
            
            modifier = "%s.%s" % ( week, period)
            description = "%s %s" % (title, modifier)

            task = Task(tw, description=description)
            task['project']=project
            task['due']=basedate+timedelta(days=weekly[period-1]-1)
            task['wait']=task['due']-timedelta(days=waitdays)

            print("%s -- due: %s -- wait until: %s" % (description, task['due'], task['wait']))

            if ( previous_task is not None ) and (dependprevious):
                task['depends'].add(previous_task)

            if ( dependson is not None ):
                try:
                    dependency = tw.tasks.filter(description='%s %s' % (dependson, modifier))[0]
                    task['depends'].add(dependency)
                except:
                    print(' -- dependency not found')
                
            if ( save ):
                task.save()
            previous_task = task
        basedate=basedate+timedelta(days=7*(1+(breakafter==week)*breakweeks))
    
if __name__ == '__main__':
    main()
