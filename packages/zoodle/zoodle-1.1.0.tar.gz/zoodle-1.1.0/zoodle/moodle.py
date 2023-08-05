from requests import session
from lxml import html

class Moodle:
    """
    Moodle client to return HTML pages for specific requests
    """

    def __init__(self, baseurl, username, password):
        """
        Create a new moodle session with given credentials
        """
        self.baseurl = baseurl
        self.session = session()
        login_payload = {
            'username': username,
            'password': password,
        }
        response = self.session.post('%s/login/index.php' % baseurl, data=login_payload)
        if "not logged in" in response.text:
            raise CredentialsError("username/password incorrect for user %s" % username)
        
    def get_user_tree(self, courseid, groupid=None, roleid=None):
        """
        Return the HTML user tree of enrolled participants
        """
        search_params = {
            'id': courseid,
            'perpage': '10000'
            }
        if groupid is not None:
            search_params['filtergroup'] = groupid
        if roleid is not None:
            search_params['role'] = roleid
        response = self.session.get(
            '%s/enrol/users.php' % ( self.baseurl ),
            params=search_params)
        return html.fromstring(response.content)
        
class CredentialsError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
