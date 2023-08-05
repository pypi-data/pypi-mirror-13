import platform
from argparse import Namespace
from functools import wraps

from keystoneclient.auth import base
from keystoneclient.session import Session
from keystoneclient.exceptions import HTTPError

from .utils import classproperty, to_json
from .resource import ResourceBase


def contrail_error_handler(f):
    """Handle HTTPErrors returned by the API server
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HTTPError as e:
            # Replace message by details to provide a
            # meaningful message
            if e.details:
                e.message, e.details = e.details, e.message
                e.args = ("%s (HTTP %s)" % (e.message, e.http_status),)
            raise
    return wrapper


class ContrailAPISession(Session):
    user_agent = "contrail-api-cli"
    protocol = None
    host = None
    port = None
    session = None
    default_headers = {
        'X-Contrail-Useragent': '%s:%s' % (platform.node(), 'contrail-api-cli'),
        "Content-Type": "application/json"
    }

    @classproperty
    def base_url(cls):
        return "%s://%s:%s" % (cls.protocol, cls.host, cls.port)

    def make_url(self, uri):
        return self.base_url + uri

    @classproperty
    def user(cls):
        return cls.session.auth.username

    @classmethod
    def make(cls, plugin_name, protocol="http", host="localhost", port=8082, **kwargs):
        """Initialize a session to Contrail API server

        @param plugin_name: auth plugin to use:
            - http: basic HTTP authentification
            - v2password: keystone v2 auth
            - v3password: keystone v3 auth
        @type plugin_name: str

        @param protocol: protocol used to connect to the API server (default: http)
        @type protocol: str
        @param host: API server host (default: localhost)
        @type host: str
        @param port: API server port (default: 8082)
        @type port: int

        @param kwargs: plugin arguments
        """
        cls.protocol = protocol
        cls.host = host
        cls.port = port
        plugin_cls = base.get_plugin_class(plugin_name)
        plugin_options = {opt.dest: kwargs.pop("os_%s" % opt.dest)
                          for opt in plugin_cls.get_options()}
        plugin = plugin_cls.load_from_options(**plugin_options)
        args = Namespace(**kwargs)
        session = cls.load_from_cli_options(args,
                                            auth=plugin)
        ResourceBase.session = session
        cls.session = session
        return session

    @contrail_error_handler
    def get_json(self, url, **kwargs):
        return self.get(url, params=kwargs).json()

    @contrail_error_handler
    def delete(self, *args, **kwargs):
        return super(ContrailAPISession, self).delete(*args, **kwargs)

    @contrail_error_handler
    def post_json(self, url, data, cls=None, **kwargs):
        """
        POST data to the api-server

        @param url: resource location (eg: "/type/uuid")
        @type url: str
        @param cls: JSONEncoder class
        @type cls: JSONEncoder
        """
        kwargs['data'] = to_json(data, cls=cls)
        kwargs['headers'] = self.default_headers
        return self.post(url, **kwargs).json()

    @contrail_error_handler
    def put_json(self, url, data, cls=None, **kwargs):
        """
        PUT data to the api-server

        @param url: resource location (eg: "/type/uuid")
        @type url: str
        @param cls: JSONEncoder class
        @type cls: JSONEncoder
        """
        kwargs['data'] = to_json(data, cls=cls)
        kwargs['headers'] = self.default_headers
        return self.put(url, **kwargs).json()

    def fqname_to_id(self, type, fq_name):
        """
        Return uuid for fq_name

        @param type: resource type
        @type type: str
        @param fq_name: resource fq name (domain:project:identifier)
        @type fq_name: str

        @rtype: UUIDv4 str
        """
        data = {
            "type": type,
            "fq_name": fq_name.split(":")
        }
        try:
            return self.post_json(self.make_url("/fqname-to-id"), data)["uuid"]
        except HTTPError:
            return None

    def id_to_fqname(self, type, uuid):
        """
        Return fq_name for uuid

        @param type: resource type
        @type type: str
        @param uuid: resource uuid
        @type uuid: UUIDv4 str

        @rtype: str (domain:project:identifier)
        """
        data = {
            "type": type,
            "uuid": uuid
        }
        try:
            fq_name = self.post_json(self.make_url("/id-to-fqname"), data)['fq_name']
            return ":".join(fq_name)
        except HTTPError:
            return None
