# Copyright (C) 2018 Phil White - All Rights Reserved
# You may use, distribute and modify this code under the
# terms of the Apache 2 license.
#
# You should have received a copy of the Apache 2 license with
# this file. If not, please visit : https://github.com/philipcwhite/monitoring2

import servicemanager
import socket
import sys
import win32event
import win32service
import win32serviceutil
import datetime
# User classes
import collect_load, collect_server, collect_settings

class CollectService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CollectService"
    _svc_display_name_ = "Collect Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        collect_server.CollectServer.send_close()

    def SvcDoRun(self):
        collect_load.load_config()
        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            collect_server.CollectServer.connection_loop()
            rc = win32event.WaitForSingleObject(self.hWaitStop, 10000)
                
if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(CollectService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(CollectService)


