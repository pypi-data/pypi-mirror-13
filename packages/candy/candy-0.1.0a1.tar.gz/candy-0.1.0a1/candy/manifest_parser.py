from lxml import etree
import xml.parsers.expat


class FirstPermissionFinder:
    """ This class is used with an expat parser to tell the location of the last
    use-permissions tag under the manifest tag. All new permissions should be added
    after that

    """
    def __init__(self, parser):
        self.parser = parser
        self.parser.EndElementHandler = self.end_element
        self.first_permission_loc = None

    def end_element(self, name) :
        if name == 'uses-permission' and self.first_permission_loc is None:
            self.first_permission_loc = self.parser.CurrentByteIndex


class ManifestEditor:
    """ A layout-preserving editor for AndroidManifest.xml"""
    def __init__(self):
        self.file_path = None
        self.root = None
        self.ns = None
        self.perm = None

    def parse(self, file_path):
        self.file_path = file_path
        with open(file_path) as f:
            self.root = etree.fromstring(f.read())
        if self.root.tag != 'manifest':
            return False
        self.ns = self.root.nsmap['android']
        attr = "{%s}name" % (self.ns, )
        self.perm = [t.attrib[attr] for t in self.root.findall('uses-permission')]
        self.perm = set(self.perm)
        return True

    def add_permissions(self, perms):
        # Remove duplicated permissions
        l = [p for p in perms if p not in self.perm]
        # Find the insertion point
        with open(self.file_path, 'rb') as f:
            parser = xml.parsers.expat.ParserCreate()
            inserter = FirstPermissionFinder(parser)
            parser.ParseFile(f)
        loc = inserter.first_permission_loc  # the insert point
        if loc is None:
            # TODO we should start the first use-permission tag
            pass
        else:
            # append
            text = ""
            for p in l:
                text += '<uses-permission android:name="%s" />\n' % (p,)
                text += '    '  # tab for the next
            with open(self.file_path, 'rb') as f:
                data = f.read()
                data = data[:loc] + text + data[loc:]
            with open(self.file_path, 'wb') as f:
                f.write(data)
        self.parse(self.file_path)

    def remove_permissions(self, perms):
        # TODO
        pass

