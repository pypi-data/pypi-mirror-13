from __future__ import division, absolute_import

__copyright__ = "Copyright (C) 2012 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


import six

import islpy as isl
from islpy import dim_type

from loopy.diagnostic import LoopyError
from pymbolic import var


def _apply_renames_in_exprs(kernel, var_renames):
    from loopy.symbolic import (
            SubstitutionRuleMappingContext,
            RuleAwareSubstitutionMapper)
    from pymbolic.mapper.substitutor import make_subst_func
    from loopy.context_matching import parse_stack_match

    srmc = SubstitutionRuleMappingContext(
            kernel.substitutions, kernel.get_var_name_generator())
    subst_map = RuleAwareSubstitutionMapper(
            srmc, make_subst_func(var_renames),
            within=parse_stack_match(None))
    return subst_map.map_kernel(kernel)


def _rename_temporaries(kernel, suffix, all_identifiers):
    var_renames = {}

    vng = kernel.get_var_name_generator()

    new_temporaries = {}
    for tv in six.itervalues(kernel.temporary_variables):
        if tv.name in all_identifiers:
            new_tv_name = vng(tv.name+suffix)
        else:
            new_tv_name = tv.name

        if new_tv_name != tv.name:
            var_renames[tv.name] = var(new_tv_name)

        assert new_tv_name not in new_temporaries
        new_temporaries[new_tv_name] = tv.copy(name=new_tv_name)

    kernel = kernel.copy(temporary_variables=new_temporaries)

    return _apply_renames_in_exprs(kernel, var_renames)


def _find_fusable_loop_domain_index(domain, other_domains):
    my_inames = set(domain.get_var_dict(dim_type.set))

    overlap_domains = []
    for i, o_dom in enumerate(other_domains):
        o_inames = set(o_dom.get_var_dict(dim_type.set))
        if my_inames & o_inames:
            overlap_domains.append(i)

    if len(overlap_domains) >= 2:
        raise LoopyError("more than one domain in one kernel has "
                "overlapping inames with a "
                "domain of the other kernel, cannot fuse: '%s'"
                % domain)

    if len(overlap_domains) == 1:
        return overlap_domains[0]
    else:
        return None


# {{{ generic merge helpers

def _ordered_merge_lists(list_a, list_b):
    result = list_a[:]
    for item in list_b:
        if item not in list_b:
            result.append(item)

    return result


def _merge_dicts(item_name, dict_a, dict_b):
    result = dict_a.copy()

    for k, v in six.iteritems(dict_b):
        if k in result:
            if v != result[k]:
                raise LoopyError("inconsistent %ss for key '%s' in merge: %s and %s"
                        % (item_name, k, v, result[k]))

        else:
            result[k] = v

    return result


def _merge_values(item_name, val_a, val_b):
    if val_a != val_b:
        raise LoopyError("inconsistent %ss in merge: %s and %s"
                % (item_name, val_a, val_b))

    return val_a

# }}}


# {{{ two-kernel fusion

def _fuse_two_kernels(knla, knlb):
    from loopy.kernel import kernel_state
    if knla.state != kernel_state.INITIAL or knlb.state != kernel_state.INITIAL:
        raise LoopyError("can only fuse kernels in INITIAL state")

    # {{{ fuse domains

    new_domains = knla.domains[:]

    for dom_b in knlb.domains:
        i_fuse = _find_fusable_loop_domain_index(dom_b, new_domains)
        if i_fuse is None:
            new_domains.append(dom_b)
        else:
            dom_a = new_domains[i_fuse]
            dom_a, dom_b = isl.align_two(dom_a, dom_b)

            shared_inames = list(
                    set(dom_a.get_var_dict(dim_type.set))
                    &
                    set(dom_b.get_var_dict(dim_type.set)))

            dom_a_s = dom_a.project_out_except(shared_inames, [dim_type.set])
            dom_b_s = dom_a.project_out_except(shared_inames, [dim_type.set])

            if not (dom_a_s <= dom_b_s and dom_b_s <= dom_a_s):
                raise LoopyError("kernels do not agree on domain of "
                        "inames '%s'" % (",".join(shared_inames)))

            new_domain = dom_a & dom_b

            new_domains[i_fuse] = new_domain

    # }}}

    vng = knla.get_var_name_generator()
    b_var_renames = {}

    # {{{ fuse args

    new_args = knla.args[:]
    for b_arg in knlb.args:
        if b_arg.name not in knla.arg_dict:
            new_arg_name = vng(b_arg.name)

            if new_arg_name != b_arg.name:
                b_var_renames[b_arg.name] = var(new_arg_name)

            new_args.append(b_arg.copy(name=new_arg_name))
        else:
            if b_arg != knla.arg_dict[b_arg.name]:
                raise LoopyError(
                        "argument '{arg_name}' has inconsistent definition between "
                        "the two kernels being merged ({arg_a} <-> {arg_b})"
                        .format(
                            arg_name=b_arg.name,
                            arg_a=str(knla.arg_dict[b_arg.name]),
                            arg_b=str(b_arg)))

    # }}}

    # {{{ fuse temporaries

    new_temporaries = knla.temporary_variables.copy()
    for b_name, b_tv in six.iteritems(knlb.temporary_variables):
        assert b_name == b_tv.name

        new_tv_name = vng(b_name)

        if new_tv_name != b_name:
            b_var_renames[b_name] = var(new_tv_name)

        assert new_tv_name not in new_temporaries
        new_temporaries[new_tv_name] = b_tv.copy(name=new_tv_name)

    # }}}

    knlb = _apply_renames_in_exprs(knlb, b_var_renames)

    # {{{ fuse instructions

    new_instructions = knla.instructions[:]
    from pytools import UniqueNameGenerator
    insn_id_gen = UniqueNameGenerator(
            set([insna.id for insna in new_instructions]))

    knl_b_instructions = []
    old_b_id_to_new_b_id = {}
    for insnb in knlb.instructions:
        old_id = insnb.id
        new_id = insn_id_gen(old_id)
        old_b_id_to_new_b_id[old_id] = new_id

        knl_b_instructions.append(
                insnb.copy(id=new_id))

    for insnb in knl_b_instructions:
        new_instructions.append(
                insnb.copy(
                    insn_deps=frozenset(
                        old_b_id_to_new_b_id[dep_id]
                        for dep_id in insnb.insn_deps)))

    # }}}

    # {{{ fuse assumptions

    assump_a = knla.assumptions
    assump_b = knlb.assumptions
    assump_a, assump_b = isl.align_two(assump_a, assump_b)

    shared_param_names = list(
            set(assump_a.get_var_dict(dim_type.set))
            &
            set(assump_b.get_var_dict(dim_type.set)))

    assump_a_s = assump_a.project_out_except(shared_param_names, [dim_type.param])
    assump_b_s = assump_a.project_out_except(shared_param_names, [dim_type.param])

    if not (assump_a_s <= assump_b_s and assump_b_s <= assump_a_s):
        raise LoopyError("assumptions do not agree on kernels to be merged")

    new_assumptions = (assump_a & assump_b).params()

    # }}}

    from loopy.kernel import LoopKernel
    return LoopKernel(
            domains=new_domains,
            instructions=new_instructions,
            args=new_args,
            name="%s_and_%s" % (knla.name, knlb.name),
            preambles=_ordered_merge_lists(knla.preambles, knlb.preambles),
            preamble_generators=_ordered_merge_lists(
                knla.preamble_generators, knlb.preamble_generators),
            assumptions=new_assumptions,
            local_sizes=_merge_dicts(
                "local size", knla.local_sizes, knlb.local_sizes),
            temporary_variables=new_temporaries,
            iname_to_tag=_merge_dicts(
                "iname-to-tag mapping",
                knla.iname_to_tag,
                knlb.iname_to_tag),
            substitutions=_merge_dicts(
                "substitution",
                knla.substitutions,
                knlb.substitutions),
            function_manglers=_ordered_merge_lists(
                knla.function_manglers,
                knlb.function_manglers),
            symbol_manglers=_ordered_merge_lists(
                knla.symbol_manglers,
                knlb.symbol_manglers),

            iname_slab_increments=_merge_dicts(
                "iname slab increment",
                knla.iname_slab_increments,
                knlb.iname_slab_increments),
            loop_priority=_ordered_merge_lists(
                knla.loop_priority,
                knlb.loop_priority),
            silenced_warnings=_ordered_merge_lists(
                knla.silenced_warnings,
                knlb.silenced_warnings),
            applied_iname_rewrites=_ordered_merge_lists(
                knla.applied_iname_rewrites,
                knlb.applied_iname_rewrites),
            index_dtype=_merge_values(
                "index dtype",
                knla.index_dtype,
                knlb.index_dtype),
            target=_merge_values(
                "target",
                knla.target,
                knlb.target),
            options=knla.options)

# }}}


def fuse_kernels(kernels, suffixes=None):
    kernels = list(kernels)

    if suffixes:
        suffixes = list(suffixes)
        if len(suffixes) != len(kernels):
            raise ValueError("length of 'suffixes' must match "
                    "length of 'kernels'")

        # {{{ rename temporaries with suffixes

        all_identifiers = [
                kernel.all_variable_names()
                for kernel in kernels]

        from functools import reduce, partial
        from operator import or_
        merge_sets = partial(reduce, or_)

        new_kernels = []
        for i, (kernel, suffix) in enumerate(zip(kernels, suffixes)):
            new_kernels.append(
                    _rename_temporaries(
                        kernel,
                        suffix,
                        merge_sets(
                            all_identifiers[:i]
                            +
                            all_identifiers[i+1:])))

        kernels = new_kernels
        del new_kernels

        # }}}

    result = kernels.pop(0)
    while kernels:
        result = _fuse_two_kernels(result, kernels.pop(0))

    return result

# vim: foldmethod=marker
