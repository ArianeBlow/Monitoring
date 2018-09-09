import wmi
import os
import socket
import pythoncom
import platform
import time
import agent_settings,agent_sql

class AgentCollect():
    async def get_data():
        # Set time
        agent_time = str(time.time()).split('.')[0]
        # Initialize WMI
        pythoncom.CoInitialize()
        c = wmi.WMI()
        # Get Hostname
        name = socket.gethostname().lower()
        # Set Return string
        output = ""

        # Configuration
        try:
            osplatform = platform.system()
            osarchitecture = platform.architecture()[0]
            osbuild = platform.win32_ver()[1]
            ipaddress = socket.gethostbyname(socket.gethostname())
            domain = socket.getfqdn().split('.', 1)[1]
            processors = str(os.cpu_count())
            await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'conf.os.name', osplatform)
            await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'conf.os.architecture', osarchitecture)
            await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'conf.os.build', osbuild)
            await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'conf.ipaddress', ipaddress)
            await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'conf.domain', domain)
            await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'conf.processors', processors)
        except:
            pass

        try:
            for i in c.Win32_ComputerSystem():
                TotalMemory = round(int(i.TotalPhysicalMemory) / 1024 / 1024, 0)
                await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'conf.memory.total', str(TotalMemory))
        except:
            pass
            

        # Filesystem
        try:
            for i in c.Win32_PerfFormattedData_PerfDisk_LogicalDisk():
                Name = i.Name.replace(':','').lower()
                PercentFreeSpace = i.PercentFreeSpace
                ActiveTime=100 - int(i.PercentIdleTime)
                if len(Name) < 3:
                    await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'perf.filesystem.' + Name + '.percent.free', str(i.PercentFreeSpace))
                    await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'perf.filesystem.' + Name + '.percent.active', str(ActiveTime))
        except:
            pass

        # Memory
        try:
            for i in c.Win32_OperatingSystem():
                FreeMem = int(i.FreePhysicalMemory)
                TotalMem = int(i.TotalVisibleMemorySize)
                PercentMem = ((TotalMem-FreeMem)/TotalMem)*100
                PercentMem = round(PercentMem,2)
                await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'perf.memory.percent.used', str(PercentMem))
        except:
            pass

        # Network
        try:    
            BytesReceivedPersec = 0
            BytesSentPersec = 0
            for i in c.Win32_PerfFormattedData_Tcpip_NetworkInterface():
                BytesReceivedPersec = BytesReceivedPersec + int(i.BytesReceivedPersec)
                BytesSentPersec = BytesSentPersec + int(i.BytesSentPersec)
                BytesReceivedPersec = BytesReceivedPersec
                BytesSentPersec = BytesSentPersec
                await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'perf.network.bytes.received', str(BytesReceivedPersec))
                await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'perf.network.bytes.sent', str(BytesSentPersec))
        except:
            pass

        # Pagefile
        try:
            for i in c.Win32_PerfFormattedData_PerfOS_PagingFile(Name = '_Total'):
                await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'perf.pagefile.percent.used', str(i.PercentUsage))
        except:
            pass

        # Processor
        try:
            for i in c.Win32_PerfFormattedData_PerfOS_Processor(Name='_Total'):
                await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'perf.processor.percent.used', str(i.PercentProcessorTime))
        except:
            pass

        # Uptime
        try:
            for i in c.Win32_PerfFormattedData_PerfOS_System():
                await agent_sql.AgentSQL.insert_agentdata(agent_time, name, 'perf.system.uptime.seconds', str(i.SystemUptime))
        except:
            pass
       
        # Service Monitoring
        try:
            if agent_settings.services:
                for service in agent_settings.services:
                    for i in c.Win32_Service(Name = service):
                        sname = 'perf.service.' + service.replace(' ','').lower() + '.state'
                        state = i.State
                        if state == 'Running':
                            state = 1
                        else:
                            state = 0
                        await agent_sql.AgentSQL.insert_agentdata(agent_time, name, sname, str(state))
        except:
            pass
        
        output = await agent_sql.AgentSQL.select_agent_data()
        return output





        




