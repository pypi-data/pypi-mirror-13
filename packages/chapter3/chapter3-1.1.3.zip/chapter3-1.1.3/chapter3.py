__author__ = 'Administrator'
import os
os.getcwd()
os.chdir('C:/Users/Administrator/Desktop/HeadFirstPython/chapter3')
# print (os.getcwd())
man = []
other = []
try:
    data = open('sketch.txt')
    data.seek(0)
    for each_line in data:
        if each_line.find(':')>0:
            try:
                (role,line_spoken) = each_line.split(':',1)
                line_spoken = line_spoken.strip()
                if role == 'Man':
                    man.append(line_spoken)
                elif role == 'Other Man':
                    other.append(line_spoken)

            except ValueError:
                pass
    data.close()
except IOError:
    print('The data file is missing!')
try:
    outman = open('mandata.out','w')
    outother = open('otherdata.out','w')
    print(man,file=outman)
    print(other,file=outother)
except IOError as err:
    print('File error: '+str(err))
finally:
    if 'outman' in locals():
        outman.close()
    if 'outother' in locals():
        outother.close()
