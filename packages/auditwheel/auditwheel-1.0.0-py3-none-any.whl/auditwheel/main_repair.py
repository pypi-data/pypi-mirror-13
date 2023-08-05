from os.path import isfile, exists, abspath
from .policy import (load_policies, get_policy_name, get_priority_by_name,
                     POLICY_PRIORITY_HIGHEST)


def configure_parser(sub_parsers):
    policy_names = [p['name'] for p in load_policies()]
    highest_policy = get_policy_name(POLICY_PRIORITY_HIGHEST)
    help = "Vendor in external shared library dependencies of a wheel."
    p = sub_parsers.add_parser('repair', help=help, description=help)
    p.add_argument('WHEEL_FILE', help='Path to wheel file.')
    p.add_argument('-f',
                   '--force',
                   help='Override symbol version ABI check',
                   action='store_true')
    p.add_argument(
        '--plat',
        dest='PLAT',
        help='Desired target platform. (default: "%s")' % highest_policy,
        choices=policy_names,
        default=highest_policy)
    p.add_argument('-L',
                   '--lib-sdir',
                   dest='LIB_SDIR',
                   help=('Subdirectory in packages to store copied libraries.'
                         ' (default: ".libs")'),
                   default='.libs')
    p.add_argument('-w',
                   '--wheel-dir',
                   dest='WHEEL_DIR',
                   type=abspath,
                   help=('Directory to store delocated wheels (default:'
                         ' "wheelhouse/")'),
                   default='wheelhouse/')
    p.set_defaults(func=execute)


def execute(args, p):
    import os
    from distutils.spawn import find_executable
    from .repair import repair_wheel
    from .wheel_abi import analyze_wheel_abi

    if not isfile(args.WHEEL_FILE):
        p.error('cannot access %s. No such file' % args.WHEEL_FILE)
    if find_executable('patchelf') is None:
        p.error('cannot find the \'patchelf\' tool, which is required')

    if not exists(args.WHEEL_DIR):
        os.makedirs(args.WHEEL_DIR)

    wheel_abi = analyze_wheel_abi(args.WHEEL_FILE)
    can_add_platform = (get_priority_by_name(args.PLAT) <=
                        get_priority_by_name(wheel_abi.sym_tag))
    if not can_add_platform:
        msg = ('cannot repair "%s" to "%s" ABI because of the presence '
               'of too-recent versioned symbols. You\'ll need to compile '
               'the wheel on an older toolchain.' %
               (args.WHEEL_FILE, args.PLAT))
        p.error(msg)

    out_wheel = repair_wheel(args.WHEEL_FILE,
                             abi=args.PLAT,
                             lib_sdir=args.LIB_SDIR,
                             out_dir=args.WHEEL_DIR)

    if out_wheel is not None:
        print('\nWriting fixed-up wheel written to %s' % out_wheel)
