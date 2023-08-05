from sbdk.commands import check_image, check_project_dir
from sbdk.docker import make_runner


def argument_parser(subparsers):
    parser = subparsers.add_parser("test", help="Test wrapper")
    parser.set_defaults(func=test)
    parser.add_argument("module", help="Python module with tests. E.g. 'sbg_wrappers.my_wrapper'. "
                                       "Same as nosetests '--where'", type=str, default='.')
    parser.add_argument("--keep-container", "-k", action='store_true',
                        help="Don't remove container when run finishes")
    parser.add_argument("--symlink-install", "-e", action='store_true',
                        help="Install wrappers with pip's -e option")


def test(project, module, keep_container=False, symlink_install=False):
    check_project_dir(project)
    check_image(project)
    r = make_runner(project)
    try:
        r.run_tests(module, remove=not keep_container, symlink=symlink_install)
    finally:
        c = r.chown()
        c.remove()


__test__ = False

