#!python

'''Script to keep track of what to do'''
import sys
import argparse
import sqlite3
import datetime
from prettytable import PrettyTable


def addTask(args, connection):
    current_time = datetime.datetime.now()
    connection.execute("INSERT INTO task (id, date_created, description, complete_status) \
                        VALUES (NULL, ?, ?, 0)", (current_time.strftime('%Y-%m-%d %H:%M'), args.descr));
    connection.commit()
    print '\'%s\' successfully added' % args.descr


def markTaskComplete(args, connection):
    connection.execute('UPDATE task SET complete_status = 1 WHERE id=?', args.id);
    connection.commit()
    print 'Task marked complete'


def listAllTasks(args, connection):
    table = PrettyTable(['Task Number', 'Task Description', 'Status'])
    table.padding_width = 1
    table.align['Task Description'] = 'l'
    table.align['Status'] = 'r'

    cursor = connection.execute('SELECT * FROM task');
    for task in cursor:
        task_number, date_added, task_description, status = task
        complete_status = getCompleteStatus(status) 
        table.add_row([task_number, task_description, complete_status])
        
    print table

        
def printTaskInfo(args, connection):
    cursor = connection.execute('SELECT * FROM task WHERE id = ?', args.id);
    for task in cursor:
        dummy, date_added, task_description, status = task
        complete_status = getCompleteStatus(status) 
        print 'Date Added:  %s' % date_added
        print 'Description: %s' % task_description
        print 'Status:      %s' % complete_status
   

def getCompleteStatus(status_complete):
    if status_complete:
        return 'COMPLETE'
    return 'NOT COMPLETE'


def createTable(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS task (id INTEGER PRIMARY KEY NOT NULL,
                                                           date_created TEXT NOT NULL,
                                                           description TEXT NOT NULL,
                                                           complete_status INTEGER NOT NULL);''')


def getParser():
    parser = argparse.ArgumentParser(description='Keeps track of the things you need to do')
    subparsers = parser.add_subparsers(dest='subparser_name')

    parser_add_task = subparsers.add_parser('addtask', help='add a new task')
    parser_add_task.add_argument('descr', help='description of task to add')
    parser_add_task.set_defaults(func=addTask)

    parser_list_tasks = subparsers.add_parser('list', help='list all tasks')
    parser_list_tasks.set_defaults(func=listAllTasks)

    parser_mark_complete = subparsers.add_parser('mrkcmp', help='mark task as complete')
    parser_mark_complete.add_argument('id', help='id number of task you want to mark as complete')
    parser_mark_complete.set_defaults(func=markTaskComplete)

    parser_get_info = subparsers.add_parser('info', help='get info on specific task')
    parser_get_info.add_argument('id', help='id number of task you want further info of') 
    parser_get_info.set_defaults(func=printTaskInfo)

    return parser


def main():
    database_connection = sqlite3.connect('task_database.db')
    createTable(database_connection)

    parser = getParser()
    args = parser.parse_args()
    args.func(args, database_connection)

    database_connection.close()


if __name__ == '__main__':
    sys.exit(main())
