#!/usr/bin/env python
import threading, subprocess, time

class MonitorDataThread(threading.Thread):

    def __init__(self, target = None, machines = []):
        threading.Thread.__init__(self)
        self.Enabled = True 
        self.function = target
        self.machines = machines
        self.store = []

    def run(self):
        if self.store == None:
            self.Enabled = False
            return
        
        try:
            while self.Enabled:
                time.sleep(10)
                self.store.extend(self.function(self.machines))
                #print "MonD :",self.store
                    
        except:
            self.Enabled = False
    

    def stop(self):
        self.Enabled = False
        self.join()
        
        return self.store

# thr = MonitorDataThread()
# thr.start()
# time.sleep(30)
# thr.stop()
# thr.join()
