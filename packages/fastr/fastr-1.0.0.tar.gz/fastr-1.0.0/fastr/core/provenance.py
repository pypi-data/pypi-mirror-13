from prov.model import ProvDocument
import fastr


class Provenance(object):
    """
    The Provenance object keeps track of everything that happens to a data object.
    """

    def __init__(self, parent, host=None):
        self.parent = parent
        if host is not None:
            self.host = host.rstrip('/')
        else:
            self.host = fastr.config.web_url()
        self.namespaces = {}
        self.document = ProvDocument()

        # Define default namespaces
        self.fastr = self._add_namespace('fastr')
        self.tool = self._add_namespace('tool')
        self.node = self._add_namespace('node')
        self.job = self._add_namespace('job')
        self.data = self._add_namespace('data')
        self.worker = self._add_namespace('worker')
        self.network = self._add_namespace('network')

        # Add fastr agent
        self.fastr_agent = self.agent(self.fastr[fastr.version.version])

    def _add_namespace(self, name, parent=None, url=None):
        if parent is None:
            host = self.host
        else:
            if parent in self.namespaces.keys():
                host = self.namespaces[parent].uri
            else:
                return None

        if url is None:
            self.namespaces[name] = self.document.add_namespace(name, "{}/{}/".format(host, name))
        else:
            self.namespaces[name] = self.document.add_namespace(name, "{}/{}".format(host, url))
        return self.namespaces[name]

    def agent(self, identifier, other_attributes=None):
        return self.document.agent(identifier, other_attributes)

    def activity(self, identifier, start_time=None, end_time=None, other_attributes=None):
        return self.document.activity(identifier, start_time, end_time, other_attributes)

    def entity(self, identifier, other_attributes=None):
        return self.document.entity(identifier, other_attributes)

