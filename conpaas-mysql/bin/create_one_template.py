#!/usr/bin/python

import sys, string

def read_template(file):
        fin = open(file, "r")
        templatestr = fin.read()
        fin.close()        
        return string.Template(templatestr)

def read_userdata(file):
        fin = open(file, "r")
        templatestr = fin.read()
        fin.close()        
        return templatestr

if __name__ == '__main__':
    file = None
    user_data = None
    if sys.argv.__len__() == 3:
        file = str(sys.argv[1])
        user_data = str(sys.argv[2])
    else:
        print "Need input [template_file] [user_data]"
        exit(1)
    template = read_template (file)
    hex_user_data=read_userdata(user_data).encode('hex')    
    template = template.substitute(USERDATA= hex_user_data, NIC = "$NIC")
    print template