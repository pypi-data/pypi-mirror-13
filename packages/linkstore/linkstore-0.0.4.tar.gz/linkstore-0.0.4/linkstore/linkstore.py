from .link_storage import SqliteLinkStorage


class Linkstore(object):
    def __init__(self, link_storage=None):
        self._storage = link_storage if link_storage is not None else SqliteLinkStorage()

    def save_link(self, an_url, tag_or_tags):
        self._storage.save(an_url, tag_or_tags)

    def find_by_tag(self, a_tag):
        return self._storage.find_by_tag(a_tag)
