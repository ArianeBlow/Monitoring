import time, datetime, socket, math, hashlib
from web_data import WebData
from web_views import WebViews

class WebAuth:
    def verify_auth(username, password):
        encrypt_password = hashlib.sha224(password.encode()).hexdigest()
        authuser = WebData.web_auth(username, encrypt_password)
        if authuser is None: return None
        else: return authuser

    def change_password(username, pass1, pass2):
        encrypt_password1 = hashlib.sha224(pass1.encode()).hexdigest()
        encrypt_password2 = hashlib.sha224(pass2.encode()).hexdigest()
        authuser = WebData.web_auth(username, encrypt_password1)
        if not authuser is None:
            WebData.web_change_password(username, encrypt_password2)
            return True
        return False

    def set_password(pass1, pass2):
        if pass1 == pass2:
            encrypt_password = hashlib.sha224(pass1.encode()).hexdigest()
            return encrypt_password

class WebIndex:
    def index_block_1():
        ok = 0
        down = 0
        total = ok + down
        uptime_check = 300
        currenttime = time.time()
        agentsystem = WebData.web_code_index_device_avail()
        for i in agentsystem:
            timestamp = int(i['timestamp'])
            if (timestamp + uptime_check) >= currenttime: ok += 1
            else: down += 1
        total = ok + down
        if total == 0: total = 1
        ok_perc = (ok / total) * 100
        down_perc = (down / total) * 100
        total_perc = str(ok_perc) + ' ' + str(down_perc)
        html = """<table style="width:100%;height:105px"><tr><td style="width:50%;text-align:center;">
        <svg width="95" height="95" viewBox="0 0 42 42" class="donut">
        <circle class="donut-ring" cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#d9534f" stroke-width="5"></circle>
        <circle class="donut-segment" cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#93C54B" stroke-width="5" stroke-dasharray='""" + total_perc +"""' stroke-dashoffset="25"></circle>
        </svg></td>
        <td style="width:50%;vertical-align:top;padding-top:34px"><svg width="10" height="10"><rect width="10" height="10" style="fill:#93C54B" /></svg> """ + str(ok) + """ Hosts Up<br />
        <svg width="10" height="10"><rect width="10" height="10" style="fill:#d9534f" /></svg> """ + str(down) + """ Hosts Down</td></tr></table>"""
        return html

    def index_block_2():
        info = 0
        warn = 0
        majr = 0
        crit = 0
        agentevents = WebData.web_code_event_totals(1)
        for i in agentevents:
            sev = int(i['severity'])
            sev_tot = int(i['total'])
            if sev == 1: crit = sev_tot
            elif sev == 2: majr = sev_tot
            elif sev == 3: warn = sev_tot
            elif sev == 4: info = sev_tot
        total = info + warn + majr + crit
        if total == 0: total = 1
        info_perc = (info / total) * 100
        warn_perc = (warn / total) * 100
        majr_perc = (majr / total) * 100
        crit_perc = (crit / total) * 100
        info_points = str(info_perc) + ' ' + str(100 - info_perc)
        warn_points = str(warn_perc) + ' ' + str(100 - warn_perc)
        majr_points = str(majr_perc) + ' ' + str(100 - majr_perc)
        crit_points = str(crit_perc) + ' ' + str(100 - crit_perc)
        html = """<table style="width:100%;height:105px"><tr><td style="width:50%;text-align:center">
        <svg width="95" height="95" viewBox="0 0 42 42" class="donut">
        <circle class="donut-ring" cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#93C54B" stroke-width="5"></circle>
        <circle class="donut-segment" cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#29ABE0" stroke-width="5" stroke-dasharray='""" + info_points +"""' stroke-dashoffset="25"></circle>
        <circle class="donut-segment" cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#ffc107" stroke-width="5" stroke-dasharray='""" + warn_points +"""' stroke-dashoffset='""" + str(100 - info_perc + 25) + """'></circle>
        <circle class="donut-segment" cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#F47C3C" stroke-width="5" stroke-dasharray='""" + majr_points +"""' stroke-dashoffset='""" + str(100 - info_perc - warn_perc + 25) + """'></circle>
        <circle class="donut-segment" cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#d9534f" stroke-width="5" stroke-dasharray='""" + crit_points +"""' stroke-dashoffset='""" + str(100 - info_perc - warn_perc - majr_perc + 25) + """'></circle>
        </svg></td><td style="width:50%;vertical-align:top;padding-top:16px">
        <svg width="10" height="10"><rect width="10" height="10" style="fill:#29ABE0" /></svg> """ + str(info) + """ Information<br />
        <svg width="10" height="10"><rect width="10" height="10" style="fill:#ffc107" /></svg> """ + str(warn) + """ Warning<br />
        <svg width="10" height="10"><rect width="10" height="10" style="fill:#F47C3C" /></svg> """ + str(majr) + """ Major<br />
        <svg width="10" height="10"><rect width="10" height="10" style="fill:#d9534f" /></svg> """ + str(crit) + """ Critical
        </td></tr></table>"""
        return html

    def index_block_3():
        name = socket.gethostname().lower()
        uptime_check = 300
        currenttime = time.time()
        agent_platform = ''
        agent_architecture = ''
        agent_timestamp = 0
        agent_processors = 0
        agent_memory = 0
        cpu_perc = 0
        mem_perc = 0
        try:
            agentsystem = WebData.web_code_device_system(name)
            agent_platform = agentsystem['platform']
            agent_architecture = agentsystem['architecture']
            agent_timestamp = agentsystem['timestamp']
            agent_processors = agentsystem['processors']
            agent_memory = agentsystem['memory']
            agent_perf = WebData.web_code_device_data_latest(name)
            for i in agent_perf:
                if i['monitor'] == 'perf.processor.percent.used' : cpu_perc = float(i['value'])
                if i['monitor'] == 'perf.memory.percent.used' : mem_perc = float(i['value'])
        except: pass
        html = """<table style="width:100%;height:105px"><tr><td style="width:50%;padding-left:25px;vertical-align:top;padding-top:10px">
        Name: """ + name + """<br />
        Processors: """ + str(agent_processors) + """<br />
        Memory: """ + str(agent_memory)[:-3] + """ MB <br />
        Platform: """ + agent_platform + """ (""" + agent_architecture + """) <br />
        </td><td style="width:50%;padding-left:10px;vertical-align:top;padding-top:10px">"""
        if (agent_timestamp + uptime_check) >= currenttime:
            cpu_color = "93C54B"
            mem_color = "93C54B"
            if cpu_perc >= 90 : cpu_color = "D9534F"
            html = html + """<svg width="10" height="10"><rect width="10" height="10" style="fill:#""" + cpu_color + """" /></svg> """ + str(cpu_perc)[:-2] + """% CPU<br />"""
            if mem_perc >= 90: mem_color = "D9534F"
            html = html + """<svg width="10" height="10"><rect width="10" height="10" style="fill:#""" + mem_color + """" /></svg> """ + str(mem_perc)[:-2] + """% Memory<br />"""
        else: html = html + "Agent Not Reporting"
        html = html + "</td></tr></table>"
        return html

    def index_block_4(page):
        page_start = (int(page) * 100) - 100
        page_end = page_start + 100
        agentsystem = WebData.web_code_index_devices(page_start, page_end)
        uptime_check = 300
        currenttime = time.time()
        html = ""
        icon = ""
        for i in agentsystem:
            dt = datetime.datetime.fromtimestamp(int(i['timestamp']))
            date = """<span style="padding-right:10px">Last Reported: """ + str(dt) + "</span>"
            color = "93C54B"
            if (int(i['timestamp']) + uptime_check) < currenttime : color = "D9534F"
            icon = """<svg width="10" height="10"><rect width="10" height="10" style="fill:#""" + color + """" /></svg>"""
            html += "<tr><td style='padding-left:20px'>" + icon + " &nbsp;<a href='devices/" + str(i['name']) + "'>" + str(i['name']) + r"</a></td><td>IP Address: " + str(i['ipaddress']) + r"</td><td>Domain: " + str(i['domain']).lower() + r"</td><td>Platform: " + str(i['platform']) + r" (" + str(i['architecture']) + r")</td><td>" + date + r"</td></tr>"
        return html

    def index_block_pager(page):
        page_start = (int(page) * 100) - 100
        page_end = page_start + 100
        agent_count = WebData.web_code_index_device_count()
        page_count = int(math.ceil(int(agent_count['total']) / 100))
        uptime_check = 300
        currenttime = time.time()
        html = ""
        icon = ""
        if page_count > 1:
            for i in range(1,page_count + 1):
                if i == page: html += """<td style="width:10px">""" + str(i) + "</td>"
                elif i == 1: html += """<td style="width:10px"><a href="/">""" + str(i) + """</a></td>"""
                else: html += """<td style="width:10px"><a href="/""" + str(i) + """">""" + str(i) + """</a></td>"""
        return html

    def index_page(index_block_1, index_block_2, index_block_3, index_block_4, index_block_pager):
        html = """<table style="width:100%;">
        <tr><td style="padding-right:4px">
        <div class="card-div"><div class="card-header">Host Availability</div>""" + index_block_1 + """</div></td>
        <td style="padding-left:4px;padding-right:4px">
        <div class="card-div"><div class="card-header">Open Events</div>""" + index_block_2 + """</div></td>
        <td style="padding-left:4px">
        <div class="card-div"><div class="card-header">Monitoring Server</div>""" + index_block_3 + """</div></td></tr>
        <tr><td colspan="3" style="padding-top:8px">
        <div class="card-div"><div class="card-header">Host Summary</div>
        <table style="width:100%;table-layout:fixed;">""" + index_block_4 + """</table> 
        <table style="width:100%;table-layout:fixed;"><tr><td></td>
        """ + index_block_pager + """
        <td style="width:10px"></td></tr>
        </table></div></td></tr></table>"""
        return html

    def index_content(page):
        html=""
        html += WebIndex.index_page(WebIndex.index_block_1(), WebIndex.index_block_2(), WebIndex.index_block_3(), WebIndex.index_block_4(page), WebIndex.index_block_pager(page))
        return html

class WebDeviceGraph:
    def __init__(self, time, dvalue):
        self.time=time
        self.dvalue=dvalue

class WebDevice:
    def device_content_system(name):
        agentsystem = WebData.web_code_device_system(name)
        html = """<table style="width:100%"><tr>
        <td><b>Name:</b> """ + agentsystem['name'] + """</td>
        <td><b>IP Address:</b> """ + agentsystem['ipaddress'] + """</td>
        <td><b>Domain:</b> """ + agentsystem['domain'].lower() + """</td>
        <td><b>Platform:</b> """ + agentsystem['platform'] + " (" + agentsystem['architecture'] + """)</td>
        <td><b>Build:</b> """ + str(agentsystem['buildnumber']) + """</td>
        <td><b>Processors:</b> """ + str(agentsystem['processors']) + """</td>
        <td><b>Memory:</b> """ + str(agentsystem['memory'])[:-3] + """ MB</td>
        </tr></table>"""
        return html

    def device_content_data(name):  
        agentsystem = WebData.web_code_device_system(name)
        agent_query = WebData.web_code_device_data_latest(name)
        cpu_perc = 0
        mem_perc = 0
        pagefile_perc = 0
        uptime_days = 0
        net_br = 0
        net_bs = 0
        fs_list = []
        for i in agent_query:
            if i['monitor'] == 'perf.processor.percent.used': cpu_perc = round(float(i['value']), 0)
            if i['monitor'] == 'perf.memory.percent.used': mem_perc = round(float(i['value']), 0)
            if i['monitor'] == 'perf.pagefile.percent.used': pagefile_perc = round(float(i['value']), 0)
            if i['monitor'] == 'perf.system.uptime.seconds': uptime_days = round(float(i['value']) / 86400, 0)
            if i['monitor'] == 'perf.network.bytes.received': net_br = round(float(i['value']), 0)
            if i['monitor'] == 'perf.network.bytes.sent': net_bs = round(float(i['value']), 0)
            if 'filesystem' in i['monitor'] and 'active' in i['monitor']:
                fs_name = i['monitor'].replace('perf.filesystem.','').replace('.percent.active','')
                fs_list.append(fs_name)
        html_fs = """<tr><td  style="padding-bottom:4px;text-align:left">
                  <div class="card-div">
                  <div class="card-header">Filesystem Monitors</div>
                  <div style="padding-left: 10px">"""
        for i in fs_list:
            try:
                fs_query_free = WebData.web_code_device_filesystem(name, 'perf.filesystem.' + i + '.percent.free')
                fs_query_active = WebData.web_code_device_filesystem(name,'perf.filesystem.' + i + '.percent.active')
                fs_free = str(round(float(fs_query_free['value']),0))
                fs_active = str(round(float(fs_query_active['value']),0))
                fs_name = ""
                if agentsystem['platform'] == 'Windows':
                    fs_name = "Windows " + i + " drive"
                elif agentsystem['platform'] == 'Linux':
                    fs_name = "Linux Filesystem: " + i             
                html_fs += """<table style="width:100%"><tr><td style="width:33%">""" + fs_name + """ drive</td>
                        <td style="width:33%"><a href="/devices/""" + name + """/perf.filesystem.""" + i + """.percent.free">Free Space: """ + fs_free + """</a></td>
                        <td style="width:33%"><a href="/devices/""" + name + """/perf.filesystem.""" + i + """.percent.active">Filesystem Activity: """ + fs_active + """</a></td>
                        </tr></table>"""
            except: pass
        html_fs += """</div></div></td></tr>""" 
        html = """<tr><td style="padding-right:4px;text-align:center">
            <div class="card-div" style="height:70px">
            <div class="card-header">Processor (% used)</div>
            <div  class="device-stats"><a class="device-stats" href="/devices/""" + name + """/perf.processor.percent.used">""" + str(cpu_perc) + """</a></div>
            </div></td>
            <td style="padding-left:4px;padding-right:4px;text-align:center">
            <div class="card-div" style="height:70px">
            <div class="card-header">Memory (% used)</div>
            <span class="device-stats"><a class="device-stats" href="/devices/""" + name + """/perf.memory.percent.used">"""  + str(mem_perc) + """</a></span>
            </div></td>
            <td style="padding-left:4px;padding-right:4px;text-align:center">
            <div class="card-div" style="height:70px">
            <div class="card-header">Pagefile (% used)</div>
            <span class="device-stats"><a class="device-stats" href="/devices/""" + name + """/perf.pagefile.percent.used">"""  + str(pagefile_perc) + """</a></span>
            </div></td>
            <td style="padding-left:4px;text-align:center">
            <div class="card-div" style="height:70px">
            <div class="card-header">Uptime (days)</div>
            <span class="device-stats"><a class="device-stats" href="/devices/""" + name + """/perf.system.uptime.seconds">"""  + str(uptime_days) + """</a></span>
            </div></td></tr></table>
            <table style="width:100%">  
            <tr><td style="padding-bottom:4px;text-align:left">
            <div class="card-div">
            <div class="card-header">Network Monitors</div>
            <div style="padding-left: 10px">
            <table style="width:100%"><tr>
            <td style="width:33%">Network Total Traffic</td>
            <td style="width:33%"><a href="/devices/""" + name + """/graph/perf.network.bytes.sent">Bytes Sent: """ + str(net_bs) + """</a></td>
            <td style="width:33%"><a href="/devices/""" + name + """/graph/perf.network.bytes.received">Bytes Received: """ + str(net_br) + """</a></td>
            </tr></table></div></div></td></tr>"""
        html += html_fs
        return html

    def device_content(name):
        html = ''
        html = WebViews.load_device_content(WebDevice.device_content_system(name), WebDevice.device_content_data(name))
        return html

    def device_graph(name, monitor):
        device_data = WebData.web_code_device_graph(name, monitor)
        data_list = []
        max_value = 0
        mid_value = 0
        graph_time = datetime.datetime.now() - datetime.timedelta(minutes=60)
        for i in range(61):
            agent_data = WebDeviceGraph(time=graph_time.strftime('%H:%M'),dvalue=0)
            data_list.append(agent_data)
            graph_time = graph_time + datetime.timedelta(minutes=1)
        for i in device_data:
            if float(i['value']) > max_value:max_value = float(i['value'])          
        for i in device_data:
            device_value = float(i['value'])
            time_short = datetime.datetime.fromtimestamp(int(i['timestamp'])).strftime('%H:%M')
            for i in data_list:
                if i.time == time_short:
                    if device_value == 0: i.dvalue = 0
                    else: i.dvalue = (device_value / max_value)*100
        device_polyline = ''
        device_polyline_data = ''
        device_time = ''
        xvalue = 55
        time_x = 0
        for i in data_list:
            dvalue = str(round(110 - i.dvalue))
            device_polyline_data += str(xvalue) + "," + dvalue + " "
            time_x += 1
            if time_x == 1:
                device_time += """<text x='""" + str(xvalue) + """' y="130" fill="#8E8C84" text-anchor="middle">""" + str(i.time) + """</text>"""
            if time_x == 5:
                time_x = 0            
            xvalue += 14 
        device_polyline = '<polyline points="' + device_polyline_data + '" style="fill:none;stroke:#29ABE0;stroke-width:1" />'                
        html =  """<svg xmlns="http://www.w3.org/2000/svg" style="color:#8E8C84;" height=150 width=990>
	    <rect x=52 y=10 width=855 height=1 fill=#ddd />
        <rect x=55 y=35 width=855 height=1 fill=#ddd />
        <rect x=52 y=60 width=855 height=1 fill=#ddd />
        <rect x=55 y=85 width=855 height=1 fill=#ddd />
        <rect x=52 y=110 width=855 height=1 fill=#ddd />
        <rect x=55 y=10 width=1 height=100 fill=#ddd />
        <text x="47" y="15" fill="#8E8C84" text-anchor="end">""" + str(int(max_value)) + """</text>
        <text x="47" y="65" fill="#8E8C84" text-anchor="end">""" + str(int(max_value / 2)) + """</text>
        <text x="47" y="115" fill="#8E8C84" text-anchor="end">0</text>
        """ + device_polyline + device_time + """
		</svg>""" 
        return html

    def device_graph_content(name, monitor):
        html = WebViews.load_basic_page("System Performance", WebDevice.device_graph(name, monitor))
        return html

class WebDevices:
    def device_index():
        agentsystem = WebData.web_code_device_all()
        uptime_check = 600
        currenttime = time.time()
        html = ""
        icon = ""
        for i in agentsystem:
            if (i['timestamp'] + uptime_check) >= currenttime: icon = """<svg width="10" height="10"><rect width="10" height="10" style="fill:#93C54B" /></svg>"""
            else: icon =  """<svg width="10" height="10"><rect width="10" height="10" style="fill:#d9534f" /></svg>"""
            html = html + """<tr><td style="padding-left:10px">""" + icon + "</td><td><a href='/devices/" + str(i['name']) + "'>" + str(i['name']) + "</td><td>" + str(i['domain']) + "</td><td>" + str(i['ipaddress']) + "</td><td>" + str(i['platform']) + "</td></tr>"
        return html

class WebEvents:
    def event_summary(status):
        total = 0
        info = 0
        warn = 0
        majr = 0
        crit = 0
        agentevents = WebData.web_code_event_totals(status)
        for i in agentevents:
            sev = int(i['severity'])
            sev_tot = int(i['total'])
            if sev == 1: crit = sev_tot
            elif sev == 2: majr = sev_tot
            elif sev == 3: warn = sev_tot
            elif sev == 4: info = sev_tot
        total = info + warn + majr + crit
        status_text = ''
        change_status = abs(int(status) - 1)
        change_status_text = ''
        if change_status == 0:
            status_text = "Open Events"
            change_status_text = "Closed Events"
        else:
            status_text = "Closed Events"
            change_status_text = "Open Events"
        html = """<table style="width:100%;text-align:center"><tr>
        <td style="text-align:left; padding-left:10px">""" + status_text + """</td>
        <td><svg width="10" height="10"><rect width="10" height="10" style="fill:#CCCCCC" /></svg>&nbsp; """ + str(total) + """&nbsp;  Total</td>
        <td><svg width="10" height="10"><rect width="10" height="10" style="fill:#29ABE0" /></svg>&nbsp;  """ + str(info) + """&nbsp;  Information</td>
        <td><svg width="10" height="10"><rect width="10" height="10" style="fill:#FFC107" /></svg>&nbsp;  """ + str(warn) + """&nbsp;  Warning</td>
        <td><svg width="10" height="10"><rect width="10" height="10" style="fill:#F47C3C" /></svg>&nbsp;  """ + str(majr) + """&nbsp;  Major</td>
        <td><svg width="10" height="10"><rect width="10" height="10" style="fill:#D9534F" /></svg>&nbsp;  """ + str(crit) + """&nbsp;  Critical</td>
        <td style="text-align:right;padding-right:12px"><input type="button" onclick="window.location.href='/events/?status=""" + str(change_status) + """'" class="action-button" value='""" + change_status_text + """' /></td>
        </tr></table>"""
        return html

    def event_list(status):
        agentevents = WebData.web_code_events(status)
        html = """<table style="width:100%">"""
        color = "#CCCCCC"
        change_status = abs(int(status) - 1)
        change_status_text = ""
        if change_status == 0: change_status_text="Close Event"
        else: change_status_text = "Open Event"
        for i in agentevents:
            date = str(datetime.datetime.fromtimestamp(int(i['timestamp'])))
            sev_text = ""
            if int(i['severity']) == 4:
                color = "#29ABE0"
                sev_text = "Information"
            elif int(i['severity']) == 3:
                color = "#FFC107"
                sev_text = "Warning"
            elif int(i['severity']) == 2:
                color = "#F47C3C"
                sev_text = "Major"
            elif int(i['severity']) == 1:
                color = "#D9534F"
                sev_text = "Critical"
            html = html + """<tr><td style="text-align:left;padding-left:10px">""" + date + """</td>
            <td style="text-align:left"><svg width="10" height="10"><rect width="10" height="10" style="fill:""" + color + """" /></svg> """ + sev_text + """</td>
            <td><a href="/device/""" + i['name'] + """">""" + i['name'] + """</a></td>
            <td>""" + i['message'] + """</td>
            <td style="text-align:right;padding-right:12px"><input type="button" onclick="window.location.href='/event_change/""" + str(i['id']) + """/""" + str(change_status) + """'" class="action-button" value='""" + change_status_text +"""'  /></td>
            </tr>"""
        html = html + "</table>"
        return html

    def events_content(status):
        html = WebViews.load_events_content(WebEvents.event_summary(status), WebEvents.event_list(status))
        return html

class WebSettings:
    def settings():
        html = """
        <b>Site Settings</b><br />
        <a href="/notify">Notification Rules</a><br />
        <br />
        <b>User and Role Management</b><br />
        <a href="/users">Manage Users</a><br />
        <br />
        <b>Documentation</b><br />
        <a href='/help'>User Guide</a><br />
        <a href="/about">About</a><br />
        <br /> """
        return html
    
    def about():
        html = """
        Copyright (C) 2018-2019 Phil White - All Rights Reserved <br />
        You may use, distribute and modify this application under the terms of the Apache 2 license. You should have received a 
        copy of the Apache 2 license with this application. If not, please visit: 
        <a href='https://github.com/philipcwhite/monitoring'>https://github.com/philipcwhite/monitoring</a>"""
        return html


class WebSearch:
    def search_devices(device):
        results = WebData.web_code_device_system_search(device)
        html = "Host names containing: " + str(device) + "<br />"
        for i in results:
            html += """<a href="/devices/""""" + str(i["name"]) + """/">""" + str(i["name"]) + "</a></br />"
        return html

class WebNotify:
    def notify_rules():
        notifyrules = WebData.web_code_select_notifyrules()
        html = "<table style='width:100%'>"
        for i in notifyrules:
            html += "<tr><td>" + str(i["notify_name"]) + """</td><td style='text-align:right;padding-right:10px'> <input type="button" onclick="window.location.href='/notify_edit/""" + str(i["id"]) + """'" class="action-button" value="Edit" />
            <input type="button" onclick="window.location.href='/notify_delete/""" + str(i["id"]) + """'" class="action-button" value="Delete" /></td></tr>"""
        html += """</table><br /><input type="button" onclick="window.location.href='/notify_add/'" class="action-button" value="Add Notification Rule" />"""
        return html

    def notify_add():
        html = """<form action='' method='POST'><table><tr><td>Rule Name</td><td><input type='text' name='notify_name' /></td></tr>
               <tr><td>Email Address</td><td><input type='text' name='notify_email' /></td></tr>"""
        dd_html = "<tr><td>Hostname</td><td><select name='agent_name'><option value='%_%'>All</option>"
        hostnames = WebData.web_code_device_system_names()
        for i in hostnames:
            dd_html += "<option value='" + str(i["name"]) + "'>" + str(i["name"]) + "</option>"
        dd_html += "</select></td></tr>"
        html += dd_html
        html += "<tr><td>Monitor</td><td><input type='text' name='agent_monitor' /></td></tr>"
        html += "<tr><td>Status</td><td><input type='radio' name='agent_status' value='1' /> Open <input type='radio' name='agent_status' value='0' /> Closed</td></tr>"
        html += "<tr><td>Severity</td><td><select name='agent_severity'><option value='4'>Information</option><option value='3'>Warning</option><option value='2'>Major</option><option value='1'>Critical</option>"
        html += "<tr><td>Enabled</td><td><input type='radio' name='notify_enabled' value='1' /> True <input type='radio' name='notify_enabled' value='0' /> False</td></tr>"
        html += "<tr><td></td><td style='text-align:right'><input type='submit' class='action-button' value='submit' /></td></tr></table>"
        return html
    
    def notify_edit(id):
        rule = WebData.web_code_select_notifyrule(id)
        html = ""
        html = """<form action='' method='POST'><table><tr><td>Rule Name</td><td><input type='text' name='notify_name' value='""" + str(rule['notify_name']) + """' /></td></tr>
               <tr><td>Email Address</td><td><input type='text' name='notify_email'  value='""" + str(rule['notify_email']) + """' /></td></tr>"""
        html += "<tr><td>Hostname</td><td><input type='text' name='agent_name' value='" + str(rule['agent_name']) + "' /></td></tr>"
        html += "<tr><td>Monitor</td><td><input type='text' name='agent_monitor' value='" + str(rule['agent_monitor']) + "' /></td></tr>"
        if int(rule['agent_status']) == 1: html += "<tr><td>Status</td><td><input type='radio' name='agent_status' value='1' checked='checked' /> Open <input type='radio' name='agent_status' value='0' /> Closed</td></tr>"
        else: html += "<tr><td>Status</td><td><input type='radio' name='agent_status' value='1' /> Open <input type='radio' name='agent_status' value='0' checked='checked' /> Closed</td></tr>"
        html += "<tr><td>Severity</td><td><select name='agent_severity'>"
        if int(rule['agent_severity']) == 4: html += "<option value='4' selected>Information</option><option value='3'>Warning</option><option value='2'>Major</option><option value='1'>Critical</option>"
        elif int(rule['agent_severity']) == 3: html += "<option value='4'>Information</option><option value='3' selected>Warning</option><option value='2'>Major</option><option value='1'>Critical</option>"
        elif int(rule['agent_severity']) == 2: html += "<option value='4'>Information</option><option value='3'>Warning</option><option value='2' selected>Major</option><option value='1'>Critical</option>"
        elif int(rule['agent_severity']) == 1: html += "<option value='4'>Information</option><option value='3'>Warning</option><option value='2'>Major</option><option value='1' selected>Critical</option>"
        if int(rule['notify_enabled']) == 1: html += "<tr><td>Enabled</td><td><input type='radio' name='notify_enabled' value='1' checked='checked' /> True <input type='radio' name='Notify_Enabled' value='0' /> False</td></tr>"
        else: html += "<tr><td>Enabled</td><td><input type='radio' name='notify_enabled' value='1' /> True <input type='radio' name='notify_enabled' value='0' checked='checked' /> False</td></tr>"      
        html += "<tr><td></td><td style='text-align:right'><input type='submit' class='action-button' value='submit' /></td></tr></table>"
        return html

class WebUsers:
    def user_initialize():
        #Check if admin user exists. If not create it
        username = 'admin'
        password = 'password'
        role = 1
        encrypt_password = hashlib.sha224(password.encode()).hexdigest()
        WebData.web_code_create_user(username, encrypt_password, role)

    def user_list():
        users = WebData.web_code_select_users()
        html = "<table style='width:100%'>"
        for i in users:
            html += "<tr><td>" + str(i["username"]) + """</td><td style='text-align:right'><input type="button" onclick="window.location.href='/user_edit_pass/""" + str(i["id"]) + """'" class="action-button" value="Password" />
            <input type="button" onclick="window.location.href='/user_edit_role/""" + str(i["id"]) + """'" class="action-button" value="Roles" />
            <input type="button" onclick="window.location.href='/user_delete/""" + str(i["id"]) + """'" class="action-button" value="Delete" />
            </td></tr>"""
        html += """</table><input type="button" onclick="window.location.href='/user_add/'" class="action-button" value="Add User" />"""
        return html

    def user_add(username, password, role):
        encrypt_password = hashlib.sha224(password.encode()).hexdigest()
        WebData.web_code_create_user(username, encrypt_password, role)

    def user_delete(id):
        WebData.web_code_delete_user(id)
