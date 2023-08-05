import candy
import sys


def usage():
    print("candy - the package/library manager for Android apps")
    print("Commands:")
    print("    install <package_name> - install a new package to the current project")
    print("    uninstall <package_name> - uninstall a given package from the current project")
    print("    search <package_name> - search a package in all known registries")


def main(argv=sys.argv):
    if len(argv) < 2:
        usage()
        return 1
    project = candy.Project('.')
    registry = candy.find_registry()
    if argv[1] == 'install':
        pkg = candy.Package.from_registry(registry, argv[2])
        project.install(pkg)
        project.fsync()
    elif argv[1] == 'uninstall':
        pkg = candy.Package.from_registry(registry, argv[2])
        project.uninstall(pkg)
        project.fsync()
    elif argv[1] == 'search':
        pkg = candy.Package.from_registry(registry, argv[2])
        if pkg is None:
            print('Package %s not found' % (argv[2],))
        else:
            print(str(pkg))
    else:
        usage()
        return 1
    return 0
