from hotdoc.core.alchemy_integration import MutableObject
from hotdoc.utils.simple_signals import Signal

class Link (MutableObject):
    resolving_link_signal = Signal()
    resolving_title_signal = Signal()
    def __init__(self, ref, title, id_):
        self._title = title
        self.ref = ref
        self.id_ = id_
        MutableObject.__init__(self)

    @property
    def title(self):
        resolved_title = Link.resolving_title_signal(self)
        resolved_title = [elem for elem in resolved_title if elem is not
                None]
        if resolved_title:
            return resolved_title[0]
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    def get_link (self):
        resolved_ref = Link.resolving_link_signal(self)
        resolved_ref = [elem for elem in resolved_ref if elem is not None]
        if resolved_ref:
            return resolved_ref[0]
        return self.ref

class LinkResolver(object):
    def __init__(self, doc_tool):
        self.__links = {}
        self.__external_links = {}
        self.doc_tool = doc_tool

    def get_named_link (self, name):
        if name in self.__links:
            return self.__links[name]

        sym = self.doc_tool.get_symbol(name)
        if sym:
            self.__links[name] = sym.link
            return sym.link

        if name in self.__external_links:
            self.__links[name] = self.__external_links[name]
            return self.__links[name]

        self.__links[name] = None
        return None

    def add_link (self, link):
        if not link.id_ in self.__links:
            self.__links[link.id_] = link

    def upsert_link (self, link, overwrite_ref=False, external=False):
        elink = self.__links.get (link.id_)

        if elink and external:
            return elink

        if external:
            self.__external_links[link.id_] = link
            return link

        if elink:
            if elink.ref is None or overwrite_ref and link.ref:
                elink.ref = link.ref
            if link.title is not None:
                elink.title = link.title
            return elink
        self.add_link (link)
        return link
