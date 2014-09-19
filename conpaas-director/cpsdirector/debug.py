import sys
from common import log

class Debug:

        def __init__(self):
                self.level = 5;

        def set_level(self, l):
                self.level = l

        def get_level(self):
                return(self.level)

        def debug(self, level, txt):
                if self.get_level() >= level:
                        try:
                                raise Exception
                        except:
                                theFrame = sys.exc_info()[2].tb_frame.f_back.f_back
                                line = theFrame.f_lineno
                                file = theFrame.f_code.co_filename
                                name = theFrame.f_code.co_name
                        log("%s: (%s) %d: %s" % (file, name, line, txt))

        def d1(self, txt):
                self.debug(1, txt);

        def d2(self, txt):
                self.debug(2, txt);

        def d3(self, txt):
                self.debug(3, txt);

        def d4(self, txt):
                self.debug(4, txt);

        def d5(self, txt):
                self.debug(5, txt);

def testing():
        di = Debug();
        for k in range(0,6,1):
            di.set_level(k)
            print "-- testing debug level %d --" % k
            di.d1("debugging level %d, d1" % k)
            di.d2("debugging level %d, d2" % k)
            di.d3("debugging level %d, d3" % k)
            di.d4("debugging level %d, d4" % k)
            di.d5("debugging level %d, d5" % k)
            print

if __name__ == '__main__':
        testing()
