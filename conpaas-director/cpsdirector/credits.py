import time
from threading import Thread, Event 
from cpsdirector import db
from cpsdirector.common import log
from cpsdirector.cloud import Resource
from cpsdirector.user import User

import logging
from conpaas.core.log import create_logger, init

from cpsdirector.iaas.controller import Controller
from datetime import datetime
# from flask import g


class Credit(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.event = Event()
        self.unit = 1
        self.charging_unit = 60
        # self.credit_step = 1
        self.credit_step = 5
        self.sanity_step = 15
        
        self.count = 0
        self.daemon = True

        self.controller = Controller()
        self.controller.setup_default()

        init('/var/log/cpsdirector/debugging.log')
        self._logger = create_logger(__name__)
        self._logger.setLevel(logging.DEBUG)

    def run(self):
        while not self.event.is_set():
            self.count += 1

            if self.count % self.credit_step == 0:
                self.check_credits()

            if self.count % self.sanity_step == 0:
                self.check_sanity()

            if self.count == max(self.credit_step, self.sanity_step):
                self.count = 0

            self.event.wait(self.unit * 60)

    def stop(self):
        self.event.set()

    
    def check_credits(self):
        from cpsdirector.application import Application
        from cpsdirector.application import _deleteapp as stop_application 
        self._logger.debug('Checking credits @%s' % datetime.now())
        # open('/tmp/miao', 'a').write('Checking credits @%s \n' % datetime.now())   
        users = User.query.all()
        for user in users:
            to_charge = 0
            rescs = Resource.query.join(Application).filter_by(user_id=user.uid)
            for res in rescs:
                created = res.created
                now = datetime.now()
                created_ts = time.mktime(created.timetuple())
                now_ts = time.mktime(now.timetuple())
                mins_from_creation = int(now_ts-created_ts) / 60
                tot_cost = mins_from_creation / self.charging_unit

                if tot_cost >= res.charged or res.charged == 0:
                    self._logger.debug('Charge for resource %s' % res.vmid)
                    # open('/tmp/miao', 'a').write('Charge for resource %s\n' % res.vmid)    
                    to_charge += tot_cost - res.charged + 1
                    res.charged += to_charge
                    # open('/tmp/miao', 'a').write('to_charge = %s\n' % to_charge)    

            user.credit -= to_charge
            if user.credit < 0:
                user.credit == 0
            if user.credit == 0:
                self._logger.debug('Stop all the applications for user %s\n' % user.uid)
                # open('/tmp/miao', 'a').write('Stop all the applications for user %s\n' % user.uid)    
                apps = Application.query.filter_by(user_id=user.uid)
                for app in apps:
                    stop_application(user.uid, app.aid, False)
                
            if to_charge != 0:
                db.session.commit()        
            



        # log('Checking credits')

    def check_sanity(self):
        self._logger.debug('Sanity check @%s' % datetime.now())
        vms = self.controller.list_vms()
        res_vmids = [res.vmid for res in Resource.query.all()]
        vms_to_remove = []
        for vm in vms:
            if vm.id not in res_vmids:
                vms_to_remove += [vm]
        
        if len(vms_to_remove) > 0:
            self.controller.delete_nodes(vms_to_remove)
        

def register_background_taks(app):
    @app.before_first_request
    def run_background_taks():
        tmr = Credit()
        tmr.start()


if __name__ == "__main__":
    tmr = Credit()
    tmr.start()
    # time.sleep(60)
    # tmr.stop()