import datetime, configparser, os, smtplib, time, pymysql.cursors
from email.message import EmailMessage

class EventSettings:
    app_path = './'
    availability_check = 300
    availability_severity = 1
    agent_retention = 2592000
    data_retention = 2592000
    event_retention = 2592000
    database = 'monitoring'
    dbhost = 'localhost'
    dbpassword = 'monitoring'
    dbuser = 'monitoring'
    mailactive = 0
    mailadmin = 'monitoring@monitoring'
    mailserver = 'localhost'
    running = True

class EventConfig:
    def load_config():
        try:
            EventSettings.running = True 
            parser = configparser.ConfigParser()
            parser.read(EventSettings.app_path + 'settings.ini')
            database = dict(parser.items('database'))
            events = dict(parser.items('events'))
            mail = dict(parser.items('mail'))
            retention = dict(parser.items('retention'))
            EventSettings.dbhost = database['host']
            EventSettings.database = database['name']
            EventSettings.dbuser = database['user']
            EventSettings.dbpassword = database['password']
            EventSettings.agent_retention = int(retention['agent'])
            EventSettings.data_retention = int(retention['data'])
            EventSettings.event_retention = int(retention['event'])
            EventSettings.mailactive = int(mail['active'])
            EventSettings.mailserver = mail['server']
            EventSettings.mailadmin = mail['admin']
            EventSettings.availability_check = int(events['availability_check'])
            EventSettings.availability_severity = int(events['availability_severity'])
        except: pass

class EventData:
    def __init__(self):
        self.con = pymysql.connect(host = EventSettings.dbhost, user = EventSettings.dbuser, password = EventSettings.dbpassword,
                                   db = EventSettings.database, charset = 'utf8mb4', cursorclass = pymysql.cursors.DictCursor)
        self.cursor = self.con.cursor()
    
    def __del__(self):
        self.con.close()

    def agent_select_id(self):
        sql = 'SELECT id from agentevents ORDER BY id DESC LIMIT 1' 
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        result = str(result['id'])
        return result
        
    def agent_events_processed(self, id):
        sql = 'UPDATE agentevents SET processed=1 WHERE id<=' + str(id)
        self.cursor.execute(sql)
        self.con.commit()

    def agent_filter_select(self, id):
        sql = '''select t1.notify_email, t1.notify_name, t2.id, t2.timestamp, t2.name, t2.monitor, t2.message, t2.severity, t2.status FROM notifyrule as t1 
                 INNER JOIN agentevents as t2 on 
                 t2.name LIKE t1.agent_name AND t2.monitor LIKE t1.agent_monitor 
                 AND t2.status LIKE t1.agent_status AND t2.severity LIKE t1.agent_severity AND t2.processed=0 AND T2.id<=''' + str(id) + ' AND t1.notify_enabled=1'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        agent_events_processed(id)
        return result
        
    def agent_avail_select(self, timestamp):
        sql = 'SELECT name FROM agentsystem WHERE timestamp < ' + timestamp
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result
        
    def agent_avail_event_open(self, timestamp, name, message, severity):
        sql = r"""INSERT INTO agentevents 
                (timestamp, name, monitor, message, status, severity, processed) 
                SELECT """ + str(timestamp) + """, '""" + name + """', 'perf.system.availability.seconds', '""" + message + """', 1, """ + str(severity) + """, 0 FROM DUAL
                WHERE NOT EXISTS (SELECT name FROM agentevents WHERE name='""" + name + """' AND monitor='perf.system.availability.seconds' AND status=1)"""
        self.cursor.execute(sql)
        self.con.commit()
           
    def agent_avail_select_event_open(self, timestamp):
        sql = r"""SELECT DISTINCT t1.name FROM agentevents as t1 
              INNER JOIN agentdata as t2 on t1.name = t2.name
              WHERE t1.monitor='perf.system.availability.seconds' AND t1.status=1 AND t2.timestamp >=""" + str(timestamp)
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if not result is None:
            for i in result:
                name = i['name']
                sql = r'UPDATE agentevents SET status=0 WHERE name="' + name + '"'
                self.cursor.execute(sql)
                self.con.commit()
        
    def remove_agents(self):
        sql = 'DELETE FROM agentsystem WHERE timestamp < ' + str(time.time() - EventSettings.agent_retention) 
        self.cursor.execute(sql)
        self.con.commit()
        
    def remove_events(self):
        sql = 'DELETE FROM agentevents WHERE timestamp < ' + str(time.time() - EventSettings.event_retention) 
        self.cursor.execute(sql)
        self.con.commit()
        
    def remove_data(self):
        sql = 'DELETE FROM agentdata WHERE timestamp < ' + str(time.time() - EventSettings.data_retention) 
        self.cursor.execute(sql)
        self.con.commit()
        
ED = EventData()

class EventAvailable:
    def check_available():
        try:
            check_time = str(time.time() - EventSettings.availability_check).split('.')[0]
            cur_time = str(time.time()).split('.')[0]
            hosts = ED.agent_avail_select(str(check_time))
            for i in hosts:
                name = i['name']
                message = 'Agent not responding for ' + str(int(round(EventSettings.availability_check / 60,0)))  + ' minutes'
                ED.agent_avail_event_open(cur_time, name, message, str(EventSettings.availability_severity))
        except: pass

    def check_open():
        try:
            check_time = str(time.time() - EventSettings.availability_check).split('.')[0]
            ED.agent_avail_select_event_open(check_time)
        except: pass

class ServerEvent:
    def process_events():
        try:
            id = ED.agent_select_id()
            output = ED.agent_filter_select(id)
            for i in output:
                notify_email = i['notify_email']
                notify_name = i['notify_name']
                name = i['name']
                monitor = i['monitor']
                message = i['message']
                severity = ''
                if i['severity'] == '1': severity = 'critical'
                if i['severity'] == '2': severity = 'major'
                if i['severity'] == '3': severity = 'warning'
                if i['severity'] == '4': severity = 'info'
                status = ''
                if i['status'] == '0': status = 'closed'
                else: status = 'open'
                timestamp = int(i['timestamp'])
                date = datetime.datetime.fromtimestamp(timestamp)
                email_subject = name + ':' + monitor + ':' + severity + ':' + status 
                email_message = '''<div style='font-family:Arial, Helvetica, sans-serif;font-size: 11pt'><b>message:</b> ''' + message + '<br /><b>name:</b> ' + name + '<br /><b>monitor:</b> ' + monitor + '<br /><b>severity:</b> ' + severity + '<br /><b>status:</b> ' + status + '<br /><b>time opened:</b> ' + str(date) + '<br /><b>policy:</b> ' + notify_name + '</div>'

                if EventSettings.mailactive == 1:
                    msg = EmailMessage()
                    msg['Subject'] = email_subject
                    msg['From'] = EventSettings.mailadmin
                    msg['To'] = notify_email
                    msg.set_content(email_message, subtype='html')
                    s = smtplib.SMTP(EventSettings.mailserver)
                    s.send_message(msg)
                    s.quit()
                f = open(EventSettings.app_path + 'output.txt','a')
                f.write(str(time.time()).split('.')[0] + ':' + notify_email + ':' + notify_name + ':' + name + ':' + monitor + ':' + message + ':' + severity + ':' +status + ':' + str(date) + '\n')
                f.close()
        except: pass

def start_server():
    EventConfig.load_config()
    while EventSettings.running == True:
        a = datetime.datetime.now().second
        if a == 0:
            EventAvailable.check_available()
            EventAvailable.check_open()
            ServerEvent.process_events()
            ED.remove_agents()
            ED.remove_data()
            ED.remove_events()
        time.sleep(1)
