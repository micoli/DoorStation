import threading

class RearmableTimer():
    def __init__(self, callback, *args, **kwargs):
        self.thread    = None
        self.callback  = callback
        self.args      = args
        self.kwargs    = kwargs
        self.rcallback = None
        self.rargs     = None
        self.rkwargs   = None
        
    def setCounterCallback(self,callback, *args, **kwargs):
        self.rcallback = callback
        self.rargs     = args
        self.rkwargs   = kwargs
        
    def repeat(self):
        if (self.thread == None):
            self.thread = threading.Timer(1.0, self.timer)
            self.thread.start()
        
    def stop(self):
        self.running=False

    def run(self,time):
        self.running=True
        self.count = time
        self.repeat()

    def timer(self):
        self.count = self.count-1
        if (self.rcallback):
            self.rcallback(self.count,*self.rargs, **self.rkwargs)
        self.thread = None
        if(self.count<=0):
            self.callback(*self.args, **self.kwargs)
        else:
            if self.running:
                self.repeat()
