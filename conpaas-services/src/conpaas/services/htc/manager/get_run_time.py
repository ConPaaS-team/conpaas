#import os
import sys
import time
import xmltodict
import pprint 
pp = pprint.PrettyPrinter(indent=4,stream=sys.stderr)

testing = False

# def poll_condor(jonbr, bagnr):
def poll_condor(filename):

    # filename = "hist-%d-%d.xml" % ( jobnr, bagnr )
    # command = "condor_history -constraint 'HtcJob == %d && HtcBag == %d' -xml > %s" % ( jobnr, bagnr, filename )
    # os.system( command )
    tries = 0
    poll_dict = {}
    while tries < 4:
        tries += 1
        _trystr = "Try %d (%s) :" % (tries, filename)
        xml = open(filename).read()
        xmldict = xmltodict.parse(xml)
        print >> sys.stderr, "type(xmldict) = ", type(xmldict)
        if not ( type(xmldict) == dict and xmldict.has_key('classads') ):
            print >> sys.stderr, _trystr, "No classads, wait a little until the first results come in"
            time.sleep(2)
            continue

        print >> sys.stderr, "type(xmldict['classads']) = ", type(xmldict['classads'])
        if not ( type(xmldict['classads']) == dict and xmldict['classads'].has_key('c') ) :
            print >> sys.stderr, _trystr, "No classads <c> entries, wait a little until the first results come in"
            time.sleep(2)
            continue

        print >> sys.stderr, "type(xmldict['classads']['c']) = ", type(xmldict['classads']['c'])
        if not ( type(xmldict['classads']['c']) == list and xmldict['classads']['c'][0].has_key('a') ) :
            print >> sys.stderr, _trystr, "No classads attributes, wait a little until the first results come in"
            time.sleep(2)
            continue
        poll_dict = get_poll_dict(xmldict)
        break
        # if poll_dict['CompletedTasks'] == poll_dict['TotalTask']:
    #pp.pprint(xmldict)
    return poll_dict


def get_poll_dict(xmldict):
        if testing:
            print >> sys.stderr, "selecting info from file %s, job %s, bag %s" % (filename, jobnr, bagnr)
        res_dict = {}
        # print >> sys.stderr, xml
        # print "----"
        # jobid = 0
        for c in xmldict['classads']['c']:
                tempdict = {}
                # pp.pprint(c)
                attrs=c['a']
                # pp.pprint(attrs)
                for d in attrs:
                        v = None
                        k = d['@n'].encode('ascii', 'ignore')   # get rid of unicode from xmltodict
                        # handle float
                        if d.has_key('r'):
                                v=float( d['r'].encode('ascii', 'ignore') )      # get rid of unicode from xmltodict
                        # handle int
                        if d.has_key('i'):
                                v=int( d['i'].encode('ascii', 'ignore') )      # get rid of unicode from xmltodict
                        # handle string
                        if d.has_key('s'):
                                # pp.pprint(d)
                                if d['s'] == None:
                                        v = 'None'
                                else:
                                        v= d['s'].encode('ascii', 'ignore')      # get rid of unicode from xmltodict
                        # handle boolean
                        if d.has_key('b'):
                                # pp.pprint(d)
                                v= 'True' if d['b']['@v'] == 't' else 'False'
                        # handle expression
                        if d.has_key('e'):
                                v= d['e'].encode('ascii', 'ignore')       # get rid of unicode from xmltodict
                        if v != None:
                                tempdict[k] = v
                        else:
                                print "unknown datatype in "
                                pp.pprint(d)
                attrdict = {}
                for k in [ 'HtcJob', 'HtcBag', 'HtcTask', 
                    'RemoteWallClockTime', 'Cmd', 
                    'MATCH_EXP_MachineCloudMachineType' ]:
                        if tempdict.has_key(k):
                            attrdict[k] = tempdict[k]
                #print kl
                # cur_jobnr = "%(HtcJob)s" % tempdict
                # if not ( jobnr == None or jobnr == cur_jobnr):
                #         continue
                # cur_bagnr = "%(HtcBag)s" % tempdict
                # if not ( bagnr == None or bagnr == cur_bagnr):
                #         continue
                # tasknr = "%(HtcTask)s" % taskdict
                taskid = "%(HtcJob)s.%(HtcBag)s.%(HtcTask)s" % tempdict
                #jobid += 1
                # print "----"
                if res_dict.has_key(taskid):
                        res_dict[taskid].append ( attrdict )
                else:
                        res_dict[taskid] = [ attrdict ]
        if testing:
            print >> sys.stderr, "====== res_dict ======"
            pp.pprint(res_dict) 
            print >> sys.stderr, "------ res_dict ------"
        return res_dict

"""


{   'tasks':
    {  
        taskid: 
        [
            {
                attr1: val1,
                attrn: valn,
            },
            {
                attr1: val1,
                attrn: valn,
            }
        ]
    }
}


"""




def do_test(filename):
        poll_dict = poll_condor(filename)
        completed_tasks = 0
        for _ in poll_dict.keys():
            completed_tasks += len(poll_dict[_])
        completed_task_sets = poll_dict.keys().__len__()
        print >> sys.stderr, "Found %d completed tasks in %d sets" % (completed_tasks, completed_task_sets)
        if False:
            pp.pprint(poll_dict)


if __name__ == "__main__":

        pp = pprint.PrettyPrinter(indent=4,stream=sys.stderr)
        testing = True
        usage = "usage : %s ClassAd_XML_file [ jobnr [ bagnr ] ]" % sys.argv[0]
        argc = len(sys.argv)
        jobnr = None
        bagnr = None
        print "%d args" % argc
        if argc <= 1:
                print usage
                filename = "test3.xml"
        if argc >= 2:
                filename = sys.argv[1]
                print "file = %s" % filename
        if argc >= 3:
                jobnr = sys.argv[2]
                print "job = %s" % jobnr
        if argc >= 4:
                bagnr = sys.argv[3]
                print "bag = %s" % bagnr

        for _ in [ "test1.xml", "test2.xml", "test3.xml", "test4.xml" ] :
            do_test( _ )
