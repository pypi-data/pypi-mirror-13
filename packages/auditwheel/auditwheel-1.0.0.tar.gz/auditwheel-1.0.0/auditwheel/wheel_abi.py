import json
import logging
import functools
from os.path import basename
from collections import defaultdict, Mapping, Sequence, namedtuple

from .genericpkgctx import InGenericPkgCtx
from .lddtree import elf_file_filter, elf_find_versioned_symbols, parse_elf
from .policy import (elf_exteral_referenences, versioned_symbols_policy,
                     max_versioned_symbol, get_policy_name,
                     POLICY_PRIORITY_LOWEST, load_policies)

log = logging.getLogger(__name__)
WheelAbIInfo = namedtuple('WheelAbIInfo',
                          ['overall_tag', 'external_refs', 'ref_tag',
                           'versioned_symbols', 'sym_tag'])


@functools.lru_cache()
def get_wheel_elfdata(wheel_fn: str):
    full_elftree = {}
    full_external_refs = {}
    versioned_symbols = defaultdict(lambda: set())

    with InGenericPkgCtx(wheel_fn) as ctx:
        for fn, elf in elf_file_filter(ctx.iter_files()):
            if elf_is_python_extension(fn, elf):
                log.info('processing: %s', fn)
                elftree = parse_elf(fn)
                full_elftree[fn] = elftree
                for key, value in elf_find_versioned_symbols(elf):
                    versioned_symbols[key].add(value)

                full_external_refs[fn] = elf_exteral_referenences(elftree,
                                                                  ctx.path)

    log.debug(json.dumps(full_elftree, indent=4))
    return (full_elftree, full_external_refs,
            max_versioned_symbol(versioned_symbols))


def analyze_wheel_abi(wheel_fn: str):
    external_refs = {
        p['name']: {'libs': {}, 'priority': p['priority']}
        for p in load_policies()}

    elftree_by_fn, external_refs_by_fn, versioned_symbols = \
            get_wheel_elfdata(wheel_fn)

    for fn, elftree in elftree_by_fn.items():
        update(external_refs, external_refs_by_fn[fn])

    log.info(json.dumps(external_refs, indent=4))
    log.debug('external referene info')
    log.debug(json.dumps(external_refs, indent=4))

    symbol_policy = versioned_symbols_policy(versioned_symbols)
    ref_policy = max(
        (e['priority'] for e in external_refs.values() if len(e['libs']) == 0),
        default=POLICY_PRIORITY_LOWEST)

    ref_tag = get_policy_name(ref_policy)
    sym_tag = get_policy_name(symbol_policy)
    overall_tag = get_policy_name(min(symbol_policy, ref_policy))

    return WheelAbIInfo(overall_tag, external_refs, ref_tag, versioned_symbols,
                        sym_tag)


def update(d, u):
    for k, v in u.items():
        if isinstance(v, Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        elif isinstance(v, (str, int, float, type(None))):
            d[k] = u[k]
        else:
            raise RuntimeError('!', d, k)
    return d


def elf_is_python_extension(fn, elf):
    modname = basename(fn).split('.', 1)[0]
    module_init_f = {'init' + modname: 2, 'PyInit_' + modname: 3}

    sect = elf.get_section_by_name(b'.dynsym')
    if sect is None:
        return False

    for sym in sect.iter_symbols():
        if (sym.name.decode('utf-8') in module_init_f and
                sym['st_shndx'] != 'SHN_UNDEF' and
                sym['st_info']['type'] == 'STT_FUNC'):

            return True

    return False
