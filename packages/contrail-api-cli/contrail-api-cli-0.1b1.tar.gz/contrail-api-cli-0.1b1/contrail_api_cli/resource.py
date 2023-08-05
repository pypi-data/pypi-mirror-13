import json
from uuid import UUID
try:
    from UserDict import UserDict
    from UserList import UserList
except ImportError:
    from collections import UserDict, UserList

from prompt_toolkit.completion import Completer, Completion

from .utils import Path, ShellContext, Observable, to_json


class ResourceEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Resource):
            return obj.data
        if isinstance(obj, Collection):
            return obj.data
        return super(ResourceEncoder, self).default(obj)


class ResourceCompleter(Completer):
    """
    Simple autocompletion on a list of resources.
    """
    def __init__(self):
        self.resources = {}
        ResourceBase.register('created', self.add_resource)
        ResourceBase.register('deleted', self.del_resource)

    def add_resource(self, resource):
        self.resources[resource.path] = resource

    def del_resource(self, resource):
        try:
            del self.resources[resource.path]
        except IndexError:
            pass

    def get_completions(self, document, complete_event):
        path_before_cursor = document.get_word_before_cursor(WORD=True).lower()

        def resource_matches(*args):
            return any([path_before_cursor in f for f in args])

        def resource_sort(resource):
            # Make the relative paths of the resource appear first in
            # the list
            if resource.type == ShellContext.current_path.base:
                return "_"
            return resource.type

        for res in sorted(self.resources.values(), key=resource_sort):
            rel_path = str(res.path.relative_to(ShellContext.current_path))
            if rel_path in ('.', '/', ''):
                continue
            if resource_matches(rel_path, res.fq_name):
                yield Completion(str(rel_path),
                                 -len(path_before_cursor),
                                 display_meta=res.fq_name)


class ResourceBase(Observable):
    session = None

    def __new__(cls, *args, **kwargs):
        if cls.session is None:
            raise ValueError("ContrailAPISession must be initialized first")
        return super(ResourceBase, cls).__new__(cls, *args, **kwargs)

    def __repr__(self):
        try:
            return repr(self.data)
        except AttributeError:
            return self.__class__.__name__


class Collection(ResourceBase, UserList):
    """Class for interacting with an API collection

    c = Collection('virtual-network', fetch=True)
    # iterate over the resources
    for r in c:
        print(r.path)
    # filter support
    c.filter("router_external", False)
    c.fetch()
    assert all([r.get('router_external') for r in c]) == False
    """

    def __init__(self, type, fetch=False, recursive=1,
                 fields=None, filters=None, parent_uuid=None,
                 **kwargs):
        """
        Base class for API collections

        @param type: name of the collection
        @type type: str
        @param fetch: immediately fetch collection from the server
        @type fetch: bool
        @param recursive: level of recursion
        @type recursive: int
        @param fields: list of field names to fetch
        @type fields: [str]
        @param filters: list of filters
        @tpye filters: [(name, value), ...]
        @param parent_uuid: filter by parent_uuid
        @type parent_uuid: v4UUID str or list of v4UUID str
        """
        UserList.__init__(self)
        self.type = type
        self.fields = fields or []
        self.filters = filters or []
        self.parent_uuid = list(self._sanitize_parent_uuid(parent_uuid))
        self.meta = dict(kwargs)
        if fetch:
            self.fetch(recursive=recursive)
        self.emit('created', self)

    @property
    def path(self):
        """Return Path of the resource

        @rtype: Path
        """
        return Path('/') / self.type

    @property
    def href(self):
        """Return collection URL

        @rtype: str
        """
        url = self.session.base_url + str(self.path)
        if self.type:
            url = url + 's'
        return url

    @property
    def fq_name(self):
        # Needed for resource completion
        return ''

    def __len__(self):
        """Return the number of items of the collection

        @rtype: int
        """
        if not self.data:
            res = self.session.get_json(self.href, count=True)
            return res[self._contrail_name]['count']
        return super(Collection, self).__len__()

    @property
    def _contrail_name(self):
        if self.type:
            return self.type + 's'
        return self.type

    def _sanitize_parent_uuid(self, parent_uuid):
        if parent_uuid is None:
            raise StopIteration
        if isinstance(parent_uuid, str):
            parent_uuid = [parent_uuid]
        for p in parent_uuid:
            try:
                UUID(p, version=4)
            except ValueError:
                continue
            yield p

    def filter(self, field_name, field_value):
        """Add permanent filter on the collection

        @param field_name: name of the field to filter on
        @type field_name: str
        @param field_value: value to filter on
        """
        self.filters.append((field_name, field_value))

    def _fetch_params(self, fields, filters, parent_uuid):
        params = {}
        fields_str = ",".join(self.fields + (fields or []))
        filters_str = ",".join(['%s==%s' % (f, json.dumps(v))
                                for f, v in self.filters + (filters or [])])
        parent_uuid_str = ",".join(self.parent_uuid +
                                   list(self._sanitize_parent_uuid(parent_uuid)))
        if fields_str:
            params['fields'] = fields_str
        if filters_str:
            params['filters'] = filters_str
        if parent_uuid_str:
            params['parent_id'] = parent_uuid_str

        return params

    def fetch(self, recursive=1, fields=None, filters=None, parent_uuid=None):
        """
        Fetch collection from API server

        @param recursive: level of recursion
        @type recursive: int
        @param fields: list of field names to fetch
        @type fields: [str]
        @param filters: list of filters
        @tpye filters: [(name, value), ...]
        @param parent_uuid: filter by parent_uuid
        @type parent_uuid: v4UUID str or list of v4UUID str
        """

        params = self._fetch_params(fields, filters, parent_uuid)
        data = self.session.get_json(self.href, **params)

        if not self.type:
            self.data = [Collection(col["link"]["name"],
                                    fetch=recursive - 1 > 0,
                                    recursive=recursive - 1,
                                    **col["link"])
                         for col in data['links']
                         if col["link"]["rel"] == "collection"]
        else:
            self.data = [Resource(self.type,
                                  fetch=recursive - 1 > 0,
                                  recursive=recursive - 1,
                                  **res)
                         for res_type, res_list in data.items()
                         for res in res_list]


class RootCollection(Collection):

    def __init__(self, **kwargs):
        return super(RootCollection, self).__init__('', **kwargs)


class Resource(ResourceBase, UserDict):
    """Class for interacting with an API resource

    r = Resource('virtual-network', uuid='4c45e89b-7780-4b78-8508-314fe04a7cbd', fetch=True)
    back_refs = list(r.back_refs)
    r['display_name'] = 'foo'
    r.save()
    r.delete()
    """

    def __init__(self, type, fetch=False, check_uuid=False, check_fq_name=True, recursive=1, **kwargs):
        """Base class for API resources

        @param type: type of the resource
        @type type: str
        @param fetch: immediately fetch resource from the server
        @type fetch: bool
        @param check_uuid: check that uuid exists on the API (makes an extra call)
        @type check_uuid: bool
        @param recursive: level of recursion
        @param recursion: int

        Either:
        @param uuid: uuid of the resource
        @type uuid: v4UUID str
        Or:
        @param fq_name: fq name of the resource
        @type fq_name: str (domain:project:identifier) or list ['domain', 'project', 'identifier']

        @raises ValueError: bad uuid or fq_name is given
        """
        self.type = type
        fq_name = kwargs.get('fq_name', None)
        if isinstance(fq_name, list):
            fq_name = ":".join(fq_name)
        elif not any([isinstance(fq_name, str), fq_name is None]):
            raise ValueError("Wrong fq_name type")
        uuid = kwargs.get('uuid', None)

        if uuid is not None:
            if check_uuid:
                fq_name = self.session.id_to_fqname(type, uuid)
                if fq_name is None:
                    raise ValueError("%s doesn't exists" % uuid)
        elif fq_name is not None:
            if check_fq_name:
                uuid = self.session.fqname_to_id(type, fq_name)
                if uuid is None:
                    raise ValueError("%s doesn't exists" % fq_name)

        if fq_name is not None:
            kwargs["fq_name"] = fq_name.split(":")
        if uuid is not None:
            kwargs["uuid"] = uuid
        UserDict.__init__(self, **kwargs)
        if self.path and self.path.is_resource and fetch:
            self.fetch(recursive=recursive)
        self.emit('created', self)

    @property
    def href(self):
        """Return URL of the resource

        @rtype: str
        """
        if self.get('href') is not None:
            return self['href']
        return self.session.base_url + str(self.path)

    @property
    def path(self):
        """Return Path of the resource

        @rtype: Path
        """
        p = Path("/") / self.type
        if self.uuid:
            return p / self.uuid
        return p

    @property
    def uuid(self):
        """Return UUID of the resource

        @rtype: v4UUID str | None
        """
        return self.get("uuid")

    @property
    def fq_name(self):
        """Return FQDN of the resource

        @rtype: str
        """
        return ":".join(self.get("fq_name", self.get("to", [])))

    def save(self):
        """Save the resource to the API server

        If the resource doesn't have a uuid the resource will be created.
        If uuid is present the resource is updated.
        """
        if self.path.is_collection:
            data = self.session.post_json(self.href + 's',
                                          {self.type: self.data},
                                          cls=ResourceEncoder)
        else:
            data = self.session.put_json(self.href, {self.type: self.data},
                                         cls=ResourceEncoder)
        self.update(data[self.type])
        self.fetch(exclude_children=True, exclude_back_refs=True)

    def delete(self):
        """Delete resource from the API server
        """
        res = self.session.delete(self.href)
        if res:
            self.emit('deleted', self)
        return res

    def fetch(self, recursive=1, exclude_children=False, exclude_back_refs=False):
        """Fetch resource from the API server

        @param recursive: level of recursion for fetching resources
        @type recursive: int
        @param exclude_children: don't get children references
        @type exclude_children: bool
        @param exclude_back_refs: don't get back_refs references
        @type exclude_back_refs: bool
        """
        data = self.session.get_json(self.href,
                                     exclude_children=exclude_children,
                                     exclude_back_refs=exclude_back_refs)[self.type]
        self.from_dict(data)

    def from_dict(self, data, recursive=1):
        """Populate the resource from a python dict

        @param recursive: level of recursion for fetching resources
        @type recursive: int
        """
        # Find other linked resources
        data = self._encode_resource(data, recursive=recursive)
        self.data.update(data)

    def _encode_resource(self, data, recursive=1):
        for attr, value in list(data.items()):
            if attr.endswith('refs'):
                res_type = "-".join([c for c in attr.split('_')
                                     if c not in ('back', 'refs')])
                for idx, r in enumerate(data[attr]):
                    data[attr][idx] = Resource(res_type,
                                               fetch=recursive - 1 > 0,
                                               recursive=recursive - 1,
                                               **data[attr][idx])
        return data

    @property
    def back_refs(self):
        """Return back_refs resources of the resource

        @rtype: Resource generator
        """
        for attr, value in self.data.items():
            if attr.endswith(('back_refs', 'loadbalancer_members')):
                for back_ref in value:
                    yield back_ref

    def json(self):
        """Return JSON representation of the resource
        """
        return to_json(self.data, cls=ResourceEncoder)

    def __str__(self):
        if hasattr(self, 'data'):
            return str(self.data)
        return str({})

    def __repr__(self):
        return 'Resource(%s,%s)' % (self.path, self)
