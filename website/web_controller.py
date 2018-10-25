import cherrypy
import web_views
from web_auth import WebAuth
from web_views import WebViews
from web_data import WebData
from web_code import WebIndex, WebDevice, WebDevices, WebEvents, WebNotify, WebSettings, WebSearch, WebUsers

user=""

class WebController:
    
    @cherrypy.expose
    def index(self, page=1):
        user=WebAuth.check_auth()
        qstring = "?page=" + str(page)
        html = WebViews.load_base(user, WebViews.load_bc_home(), WebViews.load_refresh("/index_content/" + qstring))
        return html
    
    @cherrypy.expose
    def index_content(self, page=1):
        user=WebAuth.check_auth()
        qstring = cherrypy.request.query_string
        html = WebIndex.index_content(qstring)
        return html

    @cherrypy.expose
    def events(self, status=1):
        user=WebAuth.check_auth()
        html = WebViews.load_base(user, WebViews.load_bc_events(), WebViews.load_refresh("/events_content/" + str(status)))
        return html

    @cherrypy.expose
    def events_content(self, status=1):
        user = WebAuth.check_auth()
        html = WebEvents.events_content(status)
        return html

    @cherrypy.expose
    def event_change(self, id, status):
        user = WebAuth.check_auth()
        WebData.web_code_change_event_status(id, status)
        raise cherrypy.HTTPRedirect("/events")


    @cherrypy.expose
    def devices(self, name=None, monitor=None):
        user=WebAuth.check_auth()
        if name is None and monitor is None:
            html = WebViews.load_base(user, WebViews.load_bc_devices(), WebViews.load_basic_page("Devices", WebDevices.device_index()))
        elif not name is None and monitor is None:
            html = WebViews.load_base(user, WebViews.load_bc_device(name), WebViews.load_refresh("/device_content/" + name))
        elif not name is None and not monitor is None:
            html = WebViews.load_base(user, WebViews.load_bc_device_graph(name, monitor), WebViews.load_refresh("/device_graph_content/" + name + "/" + monitor))
        return html
    
    @cherrypy.expose
    def device_content(self, name):
        user=WebAuth.check_auth()
        html = WebDevice.device_content(name)
        return html

    @cherrypy.expose
    def device_graph_content(self, name, monitor):
        user=WebAuth.check_auth()
        html = WebDevice.device_graph_content(name, monitor)
        return html

    @cherrypy.expose
    def reports(self):
        user=WebAuth.check_auth()
        html = WebViews.load_base(user, WebViews.load_bc_reports(), "reports")
        return html

    @cherrypy.expose
    def settings(self):
        user=WebAuth.check_auth()
        html = WebViews.load_base(user, WebViews.load_bc_settings(),  WebViews.load_basic_page("Settings", WebSettings.settings()))
        return html

    @cherrypy.expose
    def notify(self):
        user=WebAuth.check_auth()
        html = WebViews.load_base(user, WebViews.load_bc_settings(), WebViews.load_basic_page("Notification Rules", WebNotify.notify_rules()))
        return html
    
    @cherrypy.expose
    def notify_add(self, notify_name = None, notify_email = None, agent_name = None, agent_monitor = None, agent_status = None, agent_severity = None, notify_enabled = None):
        user=WebAuth.check_auth()
        html=""
        if notify_name is None and notify_email is None and agent_name is None and agent_monitor is None and agent_status is None and agent_severity is None and notify_enabled is None:
            html = WebViews.load_base(user, WebViews.load_bc_settings(), WebViews.load_basic_page("Add Notification Rule", WebNotify.notify_add()))
            return html
        else:
            WebData.web_code_insert_notifyrules(notify_name, notify_email, agent_name, agent_monitor, agent_status, agent_severity, notify_enabled)
            raise cherrypy.HTTPRedirect("/notify")

    @cherrypy.expose
    def notify_edit(self, id, notify_name = None, notify_email = None, agent_name = None, agent_monitor = None, agent_status = None, agent_severity = None, notify_enabled = None):
        user=WebAuth.check_auth()
        html=""
        if notify_name is None and notify_email is None and agent_name is None and agent_monitor is None and agent_status is None and agent_severity is None and notify_enabled is None:
            html = WebViews.load_base(user, WebViews.load_bc_settings(), WebViews.load_basic_page("Edit Notification Rule", WebNotify.notify_edit(id)))
            return html
        else:
            WebData.web_code_update_notifyrules(id, notify_name, notify_email, agent_name, agent_monitor, agent_status, agent_severity, notify_enabled)
            raise cherrypy.HTTPRedirect("/notify")
 
    @cherrypy.expose
    def notify_delete(self, id):
        user=WebAuth.check_auth()
        WebData.web_code_delete_notify_rule(id)
        raise cherrypy.HTTPRedirect("/notify")

    @cherrypy.expose
    def users(self):
        user=WebAuth.check_auth()
        html = WebViews.load_base(user, WebViews.load_bc_settings(), WebViews.load_basic_page("Users", WebUsers.users_list()))
        return html

    @cherrypy.expose
    def user_add(self, username=None, password=None, role=None):
        user=WebAuth.check_auth()
        if not username is None and not password is None and not role is None:
            WebUsers.user_add(username, password, role)
            raise cherrypy.HTTPRedirect("/users")
        else:
            html = WebViews.load_base(user, WebViews.load_bc_settings(), WebViews.load_basic_page("Users", WebViews.load_user_add()))
            return html

    @cherrypy.expose
    def user_edit_pass(self, id, password=None):
        user=WebAuth.check_auth()
        html = WebViews.load_base(user, WebViews.load_bc_settings(), WebViews.load_basic_page("Users", "Users"))
        return html

    @cherrypy.expose
    def user_edit_role(self, id, role=None):
        user=WebAuth.check_auth()
        html = WebViews.load_base(user, WebViews.load_bc_settings(), WebViews.load_basic_page("Users", "Users"))
        return html

    @cherrypy.expose
    def user_delete(self, id):
        user=WebAuth.check_auth()
        #Add confirmation Page
        #WebData.web_code_delete_users(id)
        raise cherrypy.HTTPRedirect("/users")
          
    @cherrypy.expose
    def search(self, device=None):
        user=WebAuth.check_auth()
        html = WebViews.load_base(user, WebViews.load_bc_settings(), WebViews.load_basic_page("Search Results", WebSearch.search_devices(device)))
        return html

    @cherrypy.expose
    def verify(self,username=None,password=None):
        WebAuth.verify_auth(username, password)

    @cherrypy.expose
    def logon(self):
        html = WebViews.load_login()
        return html

    @cherrypy.expose
    def logoff(self):
        cherrypy.session.delete()
        cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect("/logon")

    @cherrypy.expose
    def password(self, pass1=None, pass2=None):
        user=WebAuth.check_auth()
        if pass1 is None and pass2 is None:
            html = WebViews.load_base(user, WebViews.load_bc_settings(), WebViews.load_basic_page("Change Password", WebViews.load_change_password()))
            return html
        else:
            WebAuth.change_password(user, pass1, pass2)

    @cherrypy.expose
    def error(self):
        user=WebAuth.check_auth()
        html = WebViews.load_base(user, WebViews.load_bc_settings(),  WebViews.load_basic_page("Error", "Error"))
        return html
            
