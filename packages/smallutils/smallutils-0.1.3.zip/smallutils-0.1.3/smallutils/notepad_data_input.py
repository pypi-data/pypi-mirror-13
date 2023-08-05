"""
    Module to allow users to enter info to notepad and pgrm retrieve contents from notepad.

    Learnings:
        Open excel in command prompt
        http://superuser.com/questions/730249/run-command-to-open-csv-file-in-excel
        
"""
import os, re, sys
import pandas
from start_prgm_handler import spawn_program


def read_data_fr_file(filename): 
    """ Read all parameters from a file. Empty line and those with comment '#' will be ignored.
        Args:
            filename (str): full path of input.func_closure
        Returns:
            (list): list of contents.
    """
    
    with open(filename,'r') as f:
        included_para = [x.split('\n')[0] for x in f.readlines()]
        included_para = [x for x in included_para if x!=''and not re.search('^\#.*',x)]#add the # key to the search

    return included_para

def read_data_fr_notepad(working_file, clear_content_first = 0):
    """ Function to open note pad and allow user to input the data and return the data recorded upon closing
        Args:
            working_file (str): full path of the notepad txt.
        kwargs:
            clear_content_first (binary): default 0. If 1, will clear the contents.
        Returns:
            (list): list of the data. Return those without comment '#' or empty space.
    """
    if not working_file:
        print "Enter a valid file to store the notepad txt"
        raise

    #check if not file exist --> create the file and ensure dir is present
    if not os.path.isfile(working_file):
        basedir = os.path.dirname(working_file)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
            
        open(working_file, 'w').close()

    if clear_content_first:
        with open(working_file, 'w') as f:
            f.write('')
        
    # open file wait for execution
    # add '#' to those tat will be excluded
    spawn_program(working_file,
                     path = r'C:\WINDOWS\system32\notepad.exe',
                     command = 'notepad', wait_mode = os.P_WAIT)

    return read_data_fr_file(working_file)

"""
http://superuser.com/questions/730249/run-command-to-open-csv-file-in-excel

"""

def read_data_fr_csv(working_file, headerstr, excelpath = r'C:\Program Files (x86)\Microsoft Office\Office12\excel.exe'):
    """ Temp will not apppend but always open a new fle
        Args:
            working_file (str): full path of the notepad txt.
            headerstr (str): headers with each column separated by the commas.
        Kwargs:
            excelpath (str): path containing the excel.exe.
        Return:
            pandas object: Output with user data contents
        eg:
            a  = read_data_fr_csv(r'c:\data\temp\ans1.csv', 'SBR,SERIAL_NUM')

    """
    if not working_file:
        print "Enter a valid file to store the notepad txt"
        raise

    #check if not file exist --> create the file and ensure dir is present
    if not os.path.isfile(working_file):
        basedir = os.path.dirname(working_file)
        if not os.path.exists(basedir):
            os.makedirs(basedir)

    ##write the header in
    with open(working_file,'w') as f:
        f.write(headerstr)

    ## then open with Excel, wait for user to finish input then read back using pandas.
    spawn_program(working_file,
                     path = excelpath,
                     command = 'excel', wait_mode = os.P_WAIT)

    return pandas.read_csv(working_file)







