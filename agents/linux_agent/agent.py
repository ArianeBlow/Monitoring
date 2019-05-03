# Copyright (C) 2018-2019 Phil White - All Rights Reserved
# 
# You may use, distribute and modify this code under the terms of the Apache 2 license. You should have received a 
# copy of the Apache 2 license with this file. If not, please visit:  https://github.com/philipcwhite/monitoring

import datetime, os, platform, socket, sqlite3, ssl, subprocess, time

class AgentSettings:
    log = None
    name = None
    path = './'
    port = 8888
    running = True
    secure = 0
    server = '127.0.0.1'
    services = []
    time = None
    
class AgentSQL():
    def sql_con():
        database = AgentSettings.path + 'agent_sqlite.db'
        con = sqlite3.connect(database, isolation_level=None)
        return con

    def create_tables():
        sql_create_agent_data = "CREATE TABLE IF NOT EXISTS AgentData (time integer,name text,monitor text,value integer,sent integer);"
        sql_create_agent_events = "CREATE TABLE IF NOT EXISTS AgentEvents (time integer,name text,monitor text,message text,status integer,severity integer, sent integer);"
        sql_create_agent_thresholds = "CREATE TABLE IF NOT EXISTS AgentThresholds (monitor text,severity integer,threshold integer, compare text,duration integer);"
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_create_agent_data)
        c.execute(sql_create_agent_events)
        c.execute(sql_create_agent_thresholds)
        con.commit()
        con.close()

    def delete_data_events():
        agent_time = str(time.time()-604800).split('.')[0]
        sql_delete_data = "DELETE FROM AgentData WHERE time<" + agent_time
        sql_delete_events = "DELETE FROM AgentEvents WHERE status=0 AND sent=1"
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_delete_data)
        c.execute(sql_delete_events)
        con.commit()
        con.close()

    def delete_thresholds():
        sql_query = "DELETE FROM AgentThresholds"
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_query)
        con.commit()
        con.close()

    def insert_data(monitor, value):
        sql_query = "INSERT INTO AgentData(time, name, monitor, value, sent) "
        sql_query += "VALUES(" + AgentSettings.time + ",'" + AgentSettings.name + "','" + monitor + "','" + value +  "',0)"
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_query)
        con.commit()
        con.close()

    def insert_event(monitor, message, severity):
        sql_update = "UPDATE AgentEvents SET time=" + str(AgentSettings.time) + ", message='" + message + "', severity=" + str(severity) + ", sent=0 "
        sql_update += "WHERE monitor='" + monitor + "' AND " + str(severity) + "> (SELECT MAX(severity) FROM AgentEvents WHERE monitor='" + monitor + "' AND status=1)"
        sql_insert = "INSERT INTO AgentEvents(time, name, monitor, message, status, severity, sent) "
        sql_insert += "SELECT " + str(AgentSettings.time) + ",'" + AgentSettings.name + "','" + monitor + "','" + message + "',1," + str(severity) + ",0 "
        sql_insert += "WHERE NOT EXISTS(SELECT 1 FROM AgentEvents WHERE monitor='""" + monitor + """' AND status=1)"""
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_update)
        c.execute(sql_insert)
        con.commit()
        con.close()

    def insert_thresholds(monitor, severity, threshold, compare, duration):
        sql_query = "INSERT INTO AgentThresholds(monitor, severity, threshold, compare, duration) "
        sql_query += "VALUES('" + monitor + "'," + severity + "," + threshold + ",'" + compare +  "'," + duration + ")"
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_query)
        con.commit()
        con.close()

    def select_data():
        output = ''
        sql_query = "SELECT time, name, monitor, value FROM AgentData WHERE sent=0 AND monitor NOT LIKE '%perf.service%'"
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_query)
        rows = c.fetchall()
        for time, name, monitor, value in rows:
            output += str(time) + ';' + name + ';' + monitor + ';' + str(value) + '\n'
        con.commit()
        con.close()
        return output
    
    def select_data_events(time, monitor):
        sql_query = "SELECT value FROM AgentData WHERE monitor='" + monitor + "' AND time > " + str(time) 
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_query)
        rows = c.fetchall()
        con.commit()
        con.close()
        return rows

    def select_event(monitor):
        sql_query = "SELECT monitor FROM AgentEvents WHERE monitor='" + monitor + "' AND status=1" 
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_query)
        monitor = c.fetchone()
        con.commit()
        con.close()
        return monitor

    def select_open_events():
        output = ''
        sql_query = "SELECT time, name, monitor, message, status, severity FROM AgentEvents WHERE sent=0" 
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_query)
        rows = c.fetchall()
        for time, name, monitor, message, status, severity in rows:
            output = output + str(time) + ';' + name + ';event;' + monitor + ';' + message + ';' + str(status) + ';' + str(severity) + '\n'
        con.commit()
        con.close()
        return output

    def select_thresholds():
        sql_query = "SELECT monitor, severity, threshold, compare, duration FROM AgentThresholds"
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_query)
        rows = c.fetchall()
        con.commit()
        con.close()
        return rows    
    
    def update_close_data_events():
        sql_update_data = "UPDATE AgentData SET sent=1 WHERE sent=0"
        sql_update_events = "UPDATE AgentEvents SET sent=1 WHERE sent=0"
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_update_data)
        c.execute(sql_update_events)
        con.commit()
        con.close()

    def update_event(monitor, severity):
        sql_query =  "UPDATE AgentEvents SET status=0, sent=0 WHERE monitor='" + monitor + "' AND severity=" + str(severity) 
        con = AgentSQL.sql_con()
        c = con.cursor()
        c.execute(sql_query)
        con.commit()
        con.close()

class AgentLinux():
    def perf_filesystem():
        process = os.popen('''wmic path Win32_PerfFormattedData_PerfDisk_LogicalDisk WHERE "Name LIKE '%:'" get Name,PercentFreeSpace,PercentIdleTime /format:csv''')
        result = process.read()
        process.close()
        result_list = result.split('\n')
        for i in result_list:
            if not 'PercentFreeSpace' in i and ',' in i:
                ld_list = i.split(',')
                ld_name = ld_list[1].replace(':','').lower()
                AgentSQL.insert_data('perf.filesystem.' + ld_name + '.percent.free', str(ld_list[2]))
                AgentSQL.insert_data('perf.filesystem.' + ld_name + '.percent.active', str(100 - float(ld_list[3])))

    def perf_memory():
        # Updated for Linux
        output = subprocess.run('free -m', shell=True, capture_output=True, text=True).stdout.split('\n')[1].split()[1:]
        memory_used = round( (((float(output[0])-float(output[5]))/float(output[0])))*100,0)
        AgentSQL.insert_data('conf.memory.total', str(output[0]))
        AgentSQL.insert_data('perf.memory.percent.used', str(memory_used))

    def perf_network():
        nw_br = 0
        nw_bs = 0
        # WIP
        AgentSQL.insert_data('perf.network.bytes.received', str(nw_br))
        AgentSQL.insert_data('perf.network.bytes.sent', str(nw_bs))

    def perf_pagefile():
        # WIP
        AgentSQL.insert_data('perf.pagefile.percent.used', result)
    
    def perf_processor():
        # Updated for Linux
        output = subprocess.run('top -b -n2 -p1 -d.1| grep -oP "(?<=ni, ).[0-9]*.[0-9]" | tail -1', shell=True, capture_output=True, text=True).stdout
        cpu_avg = round(100 - float(output.replace('\n','')),0)
        AgentSQL.insert_data('perf.processor.percent.used', str(cpu_avg))
    
    def perf_uptime():
        # Updated for Linux
        output = subprocess.run('cat /proc/uptime', shell=True, capture_output=True, text=True).stdout.split()[0]
        uptime = int(round(float(output),0))
        AgentSQL.insert_data('perf.system.uptime.seconds', str(uptime))
    
    def perf_services():
        # Updated for Linux
        if AgentSettings.services:
            for service in AgentSettings.services:
                #service = 'systemd'
                output = subprocess.run('ps -C ' + service + ' >/dev/null && echo 1 || echo 0', shell=True, capture_output=True, text=True).stdout.replace('\n','')
                sname = 'perf.service.' + service.replace(' ','').lower() + '.state'
                AgentSQL.insert_data(sname, str(result))

class AgentProcess():
    def initialize_agent():
        AgentSettings.name = socket.gethostname().lower()
        AgentSQL.create_tables()
        AgentSQL.delete_thresholds()
        try:
            f = open(AgentSettings.path + 'settings.cfg', 'r')
            fl = f.read().split('\n')
            for i in fl:
                if i.startswith('server:'): AgentSettings.server = i[7:].replace(' ','')
                if i.startswith('port:'): AgentSettings.port = int(i[5:].replace(' ',''))
                if i.startswith('secure:'): AgentSettings.secure = int(i[7:].replace(' ',''))
                if i.startswith('log:'): AgentSettings.log = i[4:].replace(' ','')
                if i.startswith('services:'): AgentSettings.services = i[9:].replace(' ','').split(',')
                if i.startswith('thresh:'):
                    thresh = i[7:].replace(' ','').split(',')
                    AgentSQL.insert_thresholds(thresh[0], thresh[1], thresh[2], thresh[3], thresh[4])
        except: pass

    def data_process():
        try:
            domain_name = socket.getfqdn()
            if domain_name == AgentSettings.name: domain_name = 'Stand Alone'
            build_name = subprocess.run('cat /etc/os-release|grep -oP "(?<=^NAME=).*"', shell=True, capture_output=True, text=True).stdout.replace('"','').replace('\n','')
            build_version = subprocess.run('cat /etc/os-release|grep -oP "(?<=^VERSION_ID=).*"', shell=True, capture_output=True, text=True).stdout.replace('"','').replace('\n','')

            AgentSQL.insert_data('conf.os.name', platform.system())
            AgentSQL.insert_data('conf.os.architecture', platform.architecture()[0])
            AgentSQL.insert_data('conf.os.build', build_name + ' ' + build_version)
            AgentSQL.insert_data('conf.ipaddress', socket.gethostbyname(socket.gethostname()))
            AgentSQL.insert_data('conf.domain', domain_name)
            AgentSQL.insert_data('conf.processors', str(os.cpu_count()))

        except: pass
        try:
            #AgentLinux.perf_filesystem()
            AgentLinux.perf_memory()
            #AgentLinux.perf_network()
            #AgentLinux.perf_pagefile()
            AgentLinux.perf_processor()
            AgentLinux.perf_uptime()
            AgentLinux.perf_services()
        except: pass
        output = AgentSQL.select_data()
        return output
        
    def event_create(monitor, severity, threshold, compare, duration, status):
        message = monitor.replace('perf.', '').replace('.', ' ').capitalize()
        message = message + ' ' + compare + ' ' + str(threshold) + ' for ' + str(round(duration/60)) + ' minutes'
        check_monitor = AgentSQL.select_event(monitor)
        if not check_monitor is None: check_monitor=check_monitor[0]
        if check_monitor is None and status == 1: AgentSQL.insert_event(monitor, message, severity)
        elif check_monitor == monitor and status == 0: AgentSQL.update_event(monitor, severity)
        else: pass
        
    def event_process():
        agent_time_int = int(AgentSettings.time)
        agent_thresholds = AgentSQL.select_thresholds()
        a_val = 0
        b_val = 0
        for i in agent_thresholds:
            monitor = i[0]
            severity = i[1]
            threshold = int(i[2])
            compare = i[3]
            duration = i[4]
            time_window = agent_time_int - duration
            agent_data = AgentSQL.select_data_events(time_window, monitor)
            a_val = 0
            b_val = 0
            for i in agent_data:
                value = i[0]
                if compare == '>':
                    if value > threshold:
                        a_val += 1
                        b_val += 1
                    else: b_val += 1
                elif compare == '<':
                    if value < threshold:
                        a_val += 1
                        b_val += 1
                    else: b_val += 1
                elif compare == '=':
                    if value == 0 and threshold == 0:
                        a_val += 1
                        b_val += 1
                    else: b_val += 1
            if a_val == b_val and b_val != 0 :
                AgentProcess.event_create(monitor, severity, threshold, compare, duration, 1)
            else:
                AgentProcess.event_create(monitor, severity, threshold, compare, duration, 0)
        output = AgentSQL.select_open_events()
        if output is None: output = ''
        return output
        
    def send_data(message):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            if AgentSettings.secure == 1:
                context = ssl.create_default_context()
                context.options |= ssl.PROTOCOL_TLSv1_2
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                conn = context.wrap_socket(sock, server_hostname = AgentSettings.server)
                conn.connect((AgentSettings.server, AgentSettings.port))
                byte=str(message).encode()
                conn.send(byte)
                data = conn.recv(1024).decode()
                if data == 'Received': AgentSQL.update_close_data_events()
                conn.close()
            else:
                sock.connect((AgentSettings.server, AgentSettings.port))
                byte = str(message).encode()
                sock.send(byte)
                data = sock.recv(1024).decode()
                if data == 'Received': AgentSQL.update_close_data_events()
                sock.close()
        except: pass

    def run_process():
        while AgentSettings.running == True:
            a = datetime.datetime.now().second
            if a == 0:
                AgentSettings.time = str(time.time()).split('.')[0]
                send_message = AgentProcess.data_process()
                event_message = AgentProcess.event_process()
                #print(send_message, event_message)
                message = send_message + event_message
                AgentProcess.send_data(message)
                AgentSQL.delete_data_events()
            time.sleep(1)

AgentProcess.initialize_agent()
AgentProcess.run_process()
