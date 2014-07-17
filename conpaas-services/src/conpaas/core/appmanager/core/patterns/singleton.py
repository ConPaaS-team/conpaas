#!/usr/bin/env python
import thread

class SingletonParent(object):
    """
    Implement Pattern: SINGLETON
    """

    # lock object
    __lockObj = thread.allocate_lock()

    # the unique instance
    __instance = None

    def __new__(cls, *args, **kargs):
        return cls.getInstance(cls, *args, **kargs)

    def __init__(self):
        pass

    @classmethod
    def getInstance(cls, *args, **kargs):
        """
        Static method to have a reference to **THE UNIQUE** instance
        """
        # Critical section start
        cls.__lockObj.acquire()
        try:
            if cls.__instance is None:
                # (Some exception may be thrown...)
                # Initialize **the unique** instance
                cls.__instance = object.__new__(cls, *args, **kargs)

                """
                    DO YOUR STUFF HERE
                """

        finally:
            # Exit from critical section whatever happens
            cls.__lockObj.release()
        # Critical section end

        return cls.__instance
    
# 
# a = SingletonParent()
# a.bla = 7
# 
# b = SingletonParent()
# print b.bla
# print id(a), " == ", id(b), "? = > ", id(a) == id(b)