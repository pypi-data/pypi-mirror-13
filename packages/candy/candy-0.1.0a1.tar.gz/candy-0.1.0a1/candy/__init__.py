import os
import json
import gradle_parser
import manifest_parser

_HERE = os.path.dirname(__file__)


def find_registry():
    ret = ChainedRegistry()
    with open(os.path.join(_HERE, 'registry.json')) as f:
        l = json.loads(f.read())
        for r in l:
            if r['type'] == 'local':
                registry = LocalRegistry(os.path.join(_HERE, r['database_path']))
            elif r['type'] == 'web':
                registry = LocalRegistry(r['base_url'])
            else:
                print('Error: unknown registry')
                continue
            if registry.ready():
                ret.add(registry)
    return ret


class Registry:
    def __init__(self):
        pass

    def fetch_meta(self, pkg, ver):
        return None

    def ready(self):
        return False


class ChainedRegistry(Registry):
    def __init__(self):
        Registry.__init__(self)
        self.registries = []

    def add(self, registry):
        self.registries.append(registry)

    def fetch_meta(self, pkg, ver):
        for r in self.registries:
            meta = r.fetch_meta(pkg, ver)
            if meta is not None:
                return meta
        return None

    def ready(self):
        return True


class WebRegistry(Registry):
    def __init__(self, base_url):
        Registry.__init__(self)
        self.base_url = base_url

    def fetch_meta(self, pkg, ver):
        # TODO
        return None

    def ready(self):
        return False


class LocalRegistry(Registry):
    def __init__(self, database_path):
        Registry.__init__(self)
        with open(database_path) as f:
            self.database = json.loads(f.read())

    def fetch_meta(self, pkg, ver):
        # TODO check ver
        if pkg in self.database:
            return self.database[pkg]
        else:
            return None

    def ready(self):
        return True


class Project:
    PROJECT_BUILD_SCRIPT = './app/build.gradle'
    PROJECT_MANIFEST = './app/AndroidManifest.xml'

    def __init__(self, root_path):
        self.root_path = root_path
        self.gradle_parser = gradle_parser.GradleParser()
        ok = self.gradle_parser.parse(Project.PROJECT_BUILD_SCRIPT)
        if not ok:
            print('Error: failed to parse the build.gradle of the app')
        self.manifest_parser = manifest_parser.ManifestEditor()
        ok = self.manifest_parser.parse(Project.PROJECT_MANIFEST)
        if not ok:
            print('Error: failed to parse the AndroidManifest.xml of the app')

    def add_permission(self, p):
        print('Action: add permission:' + p)
        return self.manifest_parser.add_permissions([p])

    def add_gradle_dependency(self, d):
        print('Action: add gradle dependency:' + d)
        return self.gradle_parser.add_dependency(d)

    def remove_gradle_dependency(self, d):
        print('Action: remove gradle dependency:' + d)
        return self.gradle_parser.remove_dependency(d)

    def install(self, pkg):
        """ Install a package to the project
        :param pkg: the package to be installed
        """
        m = pkg.meta
        if 'gradle_depends' in m:
            for d in m['gradle_depends']:
                self.add_gradle_dependency(d)
        if 'require_permissions' in m:
            for p in m['require_permissions']:
                self.add_permission(p)

    def uninstall(self, pkg):
        """ Uninstall a package from the project.
        Gradle dependencies will be removed but permissions will stay
        :param pkg: the package to be uninstalled
        """
        m = pkg.meta
        if 'gradle_depends' in m:
            for d in m['gradle_depends']:
                self.remove_gradle_dependency(d)

    def fsync(self):
        """ Flush all results to the disk
        """
        with open(Project.PROJECT_BUILD_SCRIPT, 'w') as f:
            f.write(self.gradle_parser.output())


class Package:
    def __init__(self, meta):
        self.meta = meta

    @staticmethod
    def from_registry(registry, pkg, ver=None):
        meta = registry.fetch_meta(pkg, ver)
        return Package(meta) if meta is not None else None

    @staticmethod
    def from_local(root_path):
        meta_file = os.path.join(root_path, 'candy.json')
        if not os.path.exists(meta_file):
            return None
        with open(meta_file) as f:
            meta = f.read()
            err = Package.validate_meta(meta)
            if err is None:
                return Package(meta)
            else:
                return None

    @staticmethod
    def validate_meta(meta):
        if 'package_name' not in meta:
            return "package name not found in the meta"
        return None

    def __str__(self):
        return str(self.meta)
