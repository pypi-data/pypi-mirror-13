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
from six.moves import zip

import islpy as isl
from islpy import dim_type

from loopy.symbolic import (
        RuleAwareIdentityMapper, RuleAwareSubstitutionMapper,
        SubstitutionRuleMappingContext)
from loopy.diagnostic import LoopyError


# {{{ assume

def assume(kernel, assumptions):
    if isinstance(assumptions, str):
        assumptions_set_str = "[%s] -> { : %s}" \
                % (",".join(s for s in kernel.outer_params()),
                    assumptions)
        assumptions = isl.BasicSet.read_from_str(kernel.domains[0].get_ctx(),
                assumptions_set_str)

    if not isinstance(assumptions, isl.BasicSet):
        raise TypeError("'assumptions' must be a BasicSet or a string")

    old_assumptions, new_assumptions = isl.align_two(kernel.assumptions, assumptions)

    return kernel.copy(
            assumptions=old_assumptions.params() & new_assumptions.params())

# }}}


# {{{ set loop priority

def set_loop_priority(kernel, loop_priority):
    """Indicates the textual order in which loops should be entered in the
    kernel code. Note that this priority has an advisory role only. If the
    kernel logically requires a different nesting, priority is ignored.
    Priority is only considered if loop nesting is ambiguous.

    :arg: an iterable of inames, or, for brevity, a comma-seaprated string of
        inames
    """

    if isinstance(loop_priority, str):
        loop_priority = [s.strip() for s in loop_priority.split(",")]

    return kernel.copy(loop_priority=loop_priority)

# }}}


# {{{ split inames

class _InameSplitter(RuleAwareIdentityMapper):
    def __init__(self, rule_mapping_context, within,
            split_iname, outer_iname, inner_iname, replacement_index):
        super(_InameSplitter, self).__init__(rule_mapping_context)

        self.within = within

        self.split_iname = split_iname
        self.outer_iname = outer_iname
        self.inner_iname = inner_iname

        self.replacement_index = replacement_index

    def map_reduction(self, expr, expn_state):
        if (self.split_iname in expr.inames
                and self.split_iname not in expn_state.arg_context
                and self.within(
                    expn_state.kernel,
                    expn_state.instruction,
                    expn_state.stack)):
            new_inames = list(expr.inames)
            new_inames.remove(self.split_iname)
            new_inames.extend([self.outer_iname, self.inner_iname])

            from loopy.symbolic import Reduction
            return Reduction(expr.operation, tuple(new_inames),
                        self.rec(expr.expr, expn_state))
        else:
            return super(_InameSplitter, self).map_reduction(expr, expn_state)

    def map_variable(self, expr, expn_state):
        if (expr.name == self.split_iname
                and self.split_iname not in expn_state.arg_context
                and self.within(
                    expn_state.kernel,
                    expn_state.instruction,
                    expn_state.stack)):
            return self.replacement_index
        else:
            return super(_InameSplitter, self).map_variable(expr, expn_state)


def split_iname(kernel, split_iname, inner_length,
        outer_iname=None, inner_iname=None,
        outer_tag=None, inner_tag=None,
        slabs=(0, 0), do_tagged_check=True,
        within=None):
    """
    :arg within: a stack match as understood by
        :func:`loopy.context_matching.parse_stack_match`.
    """

    existing_tag = kernel.iname_to_tag.get(split_iname)
    from loopy.kernel.data import ForceSequentialTag
    if do_tagged_check and (
            existing_tag is not None
            and not isinstance(existing_tag, ForceSequentialTag)):
        raise LoopyError("cannot split already tagged iname '%s'" % split_iname)

    if split_iname not in kernel.all_inames():
        raise ValueError("cannot split loop for unknown variable '%s'" % split_iname)

    applied_iname_rewrites = kernel.applied_iname_rewrites[:]

    vng = kernel.get_var_name_generator()

    if outer_iname is None:
        outer_iname = vng(split_iname+"_outer")
    if inner_iname is None:
        inner_iname = vng(split_iname+"_inner")

    def process_set(s):
        var_dict = s.get_var_dict()

        if split_iname not in var_dict:
            return s

        orig_dim_type, _ = var_dict[split_iname]

        outer_var_nr = s.dim(orig_dim_type)
        inner_var_nr = s.dim(orig_dim_type)+1

        s = s.add_dims(orig_dim_type, 2)
        s = s.set_dim_name(orig_dim_type, outer_var_nr, outer_iname)
        s = s.set_dim_name(orig_dim_type, inner_var_nr, inner_iname)

        from loopy.isl_helpers import make_slab

        space = s.get_space()
        inner_constraint_set = (
                make_slab(space, inner_iname, 0, inner_length)
                # name = inner + length*outer
                .add_constraint(isl.Constraint.eq_from_names(
                    space, {
                        split_iname: 1,
                        inner_iname: -1,
                        outer_iname: -inner_length})))

        name_dim_type, name_idx = space.get_var_dict()[split_iname]
        s = s.intersect(inner_constraint_set)

        if within is None:
            s = s.project_out(name_dim_type, name_idx, 1)

        return s

    new_domains = [process_set(dom) for dom in kernel.domains]

    from pymbolic import var
    inner = var(inner_iname)
    outer = var(outer_iname)
    new_loop_index = inner + outer*inner_length

    subst_map = {var(split_iname): new_loop_index}
    applied_iname_rewrites.append(subst_map)

    # {{{ update forced_iname deps

    new_insns = []
    for insn in kernel.instructions:
        if split_iname in insn.forced_iname_deps:
            new_forced_iname_deps = (
                    (insn.forced_iname_deps.copy()
                    - frozenset([split_iname]))
                    | frozenset([outer_iname, inner_iname]))
        else:
            new_forced_iname_deps = insn.forced_iname_deps

        insn = insn.copy(
                forced_iname_deps=new_forced_iname_deps)

        new_insns.append(insn)

    # }}}

    iname_slab_increments = kernel.iname_slab_increments.copy()
    iname_slab_increments[outer_iname] = slabs

    new_loop_priority = []
    for prio_iname in kernel.loop_priority:
        if prio_iname == split_iname:
            new_loop_priority.append(outer_iname)
            new_loop_priority.append(inner_iname)
        else:
            new_loop_priority.append(prio_iname)

    kernel = kernel.copy(
            domains=new_domains,
            iname_slab_increments=iname_slab_increments,
            instructions=new_insns,
            applied_iname_rewrites=applied_iname_rewrites,
            loop_priority=new_loop_priority)

    from loopy.context_matching import parse_stack_match
    within = parse_stack_match(within)

    rule_mapping_context = SubstitutionRuleMappingContext(
            kernel.substitutions, kernel.get_var_name_generator())
    ins = _InameSplitter(rule_mapping_context, within,
            split_iname, outer_iname, inner_iname, new_loop_index)

    kernel = ins.map_kernel(kernel)
    kernel = rule_mapping_context.finish_kernel(kernel)

    if existing_tag is not None:
        kernel = tag_inames(kernel,
                {outer_iname: existing_tag, inner_iname: existing_tag})

    return tag_inames(kernel, {outer_iname: outer_tag, inner_iname: inner_tag})

# }}}


# {{{ join inames

class _InameJoiner(RuleAwareSubstitutionMapper):
    def __init__(self, rule_mapping_context, within, subst_func,
            joined_inames, new_iname):
        super(_InameJoiner, self).__init__(rule_mapping_context,
                subst_func, within)

        self.joined_inames = set(joined_inames)
        self.new_iname = new_iname

    def map_reduction(self, expr, expn_state):
        expr_inames = set(expr.inames)
        overlap = (self.join_inames & expr_inames
                - set(expn_state.arg_context))
        if overlap and self.within(
                expn_state.kernel,
                expn_state.instruction,
                expn_state.stack):
            if overlap != expr_inames:
                raise LoopyError(
                        "Cannot join inames '%s' if there is a reduction "
                        "that does not use all of the inames being joined. "
                        "(Found one with just '%s'.)"
                        % (
                            ", ".join(self.joined_inames),
                            ", ".join(expr_inames)))

            new_inames = expr_inames - self.joined_inames
            new_inames.add(self.new_iname)

            from loopy.symbolic import Reduction
            return Reduction(expr.operation, tuple(new_inames),
                        self.rec(expr.expr, expn_state))
        else:
            return super(_InameJoiner, self).map_reduction(expr, expn_state)


def join_inames(kernel, inames, new_iname=None, tag=None, within=None):
    """
    :arg inames: fastest varying last
    :arg within: a stack match as understood by
        :func:`loopy.context_matching.parse_stack_match`.
    """

    # now fastest varying first
    inames = inames[::-1]

    if new_iname is None:
        new_iname = kernel.get_var_name_generator()("_and_".join(inames))

    from loopy.kernel.tools import DomainChanger
    domch = DomainChanger(kernel, frozenset(inames))
    for iname in inames:
        if kernel.get_home_domain_index(iname) != domch.leaf_domain_index:
            raise LoopyError("iname '%s' is not 'at home' in the "
                    "join's leaf domain" % iname)

    new_domain = domch.domain
    new_dim_idx = new_domain.dim(dim_type.set)
    new_domain = new_domain.add_dims(dim_type.set, 1)
    new_domain = new_domain.set_dim_name(dim_type.set, new_dim_idx, new_iname)

    joint_aff = zero = isl.Aff.zero_on_domain(new_domain.space)
    subst_dict = {}
    base_divisor = 1

    from pymbolic import var

    for i, iname in enumerate(inames):
        iname_dt, iname_idx = zero.get_space().get_var_dict()[iname]
        iname_aff = zero.add_coefficient_val(iname_dt, iname_idx, 1)

        joint_aff = joint_aff + base_divisor*iname_aff

        bounds = kernel.get_iname_bounds(iname, constants_only=True)

        from loopy.isl_helpers import (
                static_max_of_pw_aff, static_value_of_pw_aff)
        from loopy.symbolic import pw_aff_to_expr

        length = int(pw_aff_to_expr(
            static_max_of_pw_aff(bounds.size, constants_only=True)))

        try:
            lower_bound_aff = static_value_of_pw_aff(
                    bounds.lower_bound_pw_aff.coalesce(),
                    constants_only=False)
        except Exception as e:
            raise type(e)("while finding lower bound of '%s': " % iname)

        my_val = var(new_iname) // base_divisor
        if i+1 < len(inames):
            my_val %= length
        my_val += pw_aff_to_expr(lower_bound_aff)
        subst_dict[iname] = my_val

        base_divisor *= length

    from loopy.isl_helpers import iname_rel_aff
    new_domain = new_domain.add_constraint(
            isl.Constraint.equality_from_aff(
                iname_rel_aff(new_domain.get_space(), new_iname, "==", joint_aff)))

    for i, iname in enumerate(inames):
        iname_to_dim = new_domain.get_space().get_var_dict()
        iname_dt, iname_idx = iname_to_dim[iname]

        if within is None:
            new_domain = new_domain.project_out(iname_dt, iname_idx, 1)

    def subst_forced_iname_deps(fid):
        result = set()
        for iname in fid:
            if iname in inames:
                result.add(new_iname)
            else:
                result.add(iname)

        return frozenset(result)

    new_insns = [
            insn.copy(
                forced_iname_deps=subst_forced_iname_deps(insn.forced_iname_deps))
            for insn in kernel.instructions]

    kernel = (kernel
            .copy(
                instructions=new_insns,
                domains=domch.get_domains_with(new_domain),
                applied_iname_rewrites=kernel.applied_iname_rewrites + [subst_dict]
                ))

    from loopy.context_matching import parse_stack_match
    within = parse_stack_match(within)

    from pymbolic.mapper.substitutor import make_subst_func
    rule_mapping_context = SubstitutionRuleMappingContext(
            kernel.substitutions, kernel.get_var_name_generator())
    ijoin = _InameJoiner(rule_mapping_context, within,
            make_subst_func(subst_dict),
            inames, new_iname)

    kernel = rule_mapping_context.finish_kernel(
            ijoin.map_kernel(kernel))

    if tag is not None:
        kernel = tag_inames(kernel, {new_iname: tag})

    return kernel

# }}}


# {{{ tag inames

def tag_inames(kernel, iname_to_tag, force=False, ignore_nonexistent=False):
    from loopy.kernel.data import parse_tag

    iname_to_tag = dict((iname, parse_tag(tag))
            for iname, tag in six.iteritems(iname_to_tag))

    from loopy.kernel.data import (ParallelTag, AutoLocalIndexTagBase,
            ForceSequentialTag)

    new_iname_to_tag = kernel.iname_to_tag.copy()
    for iname, new_tag in six.iteritems(iname_to_tag):
        if iname not in kernel.all_inames():
            if ignore_nonexistent:
                continue
            else:
                raise LoopyError("iname '%s' does not exist" % iname)

        old_tag = kernel.iname_to_tag.get(iname)

        retag_ok = False

        if isinstance(old_tag, (AutoLocalIndexTagBase, ForceSequentialTag)):
            retag_ok = True

        if not retag_ok and old_tag is not None and new_tag is None:
            raise ValueError("cannot untag iname '%s'" % iname)

        if iname not in kernel.all_inames():
            raise ValueError("cannot tag '%s'--not known" % iname)

        if isinstance(new_tag, ParallelTag) \
                and isinstance(old_tag, ForceSequentialTag):
            raise ValueError("cannot tag '%s' as parallel--"
                    "iname requires sequential execution" % iname)

        if isinstance(new_tag, ForceSequentialTag) \
                and isinstance(old_tag, ParallelTag):
            raise ValueError("'%s' is already tagged as parallel, "
                    "but is now prohibited from being parallel "
                    "(likely because of participation in a precompute or "
                    "a reduction)" % iname)

        if (not retag_ok) and (not force) \
                and old_tag is not None and (old_tag != new_tag):
            raise LoopyError("'%s' is already tagged '%s'--cannot retag"
                    % (iname, old_tag))

        new_iname_to_tag[iname] = new_tag

    return kernel.copy(iname_to_tag=new_iname_to_tag)

# }}}


# {{{ duplicate inames

class _InameDuplicator(RuleAwareIdentityMapper):
    def __init__(self, rule_mapping_context,
            old_to_new, within):
        super(_InameDuplicator, self).__init__(rule_mapping_context)

        self.old_to_new = old_to_new
        self.old_inames_set = set(six.iterkeys(old_to_new))
        self.within = within

    def map_reduction(self, expr, expn_state):
        if (set(expr.inames) & self.old_inames_set
                and self.within(
                    expn_state.kernel,
                    expn_state.instruction,
                    expn_state.stack)):
            new_inames = tuple(
                    self.old_to_new.get(iname, iname)
                    if iname not in expn_state.arg_context
                    else iname
                    for iname in expr.inames)

            from loopy.symbolic import Reduction
            return Reduction(expr.operation, new_inames,
                        self.rec(expr.expr, expn_state))
        else:
            return super(_InameDuplicator, self).map_reduction(expr, expn_state)

    def map_variable(self, expr, expn_state):
        new_name = self.old_to_new.get(expr.name)

        if (new_name is None
                or expr.name in expn_state.arg_context
                or not self.within(
                    expn_state.kernel,
                    expn_state.instruction,
                    expn_state.stack)):
            return super(_InameDuplicator, self).map_variable(expr, expn_state)
        else:
            from pymbolic import var
            return var(new_name)

    def map_instruction(self, kernel, insn):
        if not self.within(kernel, insn, ()):
            return insn

        new_fid = frozenset(
                self.old_to_new.get(iname, iname)
                for iname in insn.forced_iname_deps)
        return insn.copy(forced_iname_deps=new_fid)


def duplicate_inames(knl, inames, within, new_inames=None, suffix=None,
        tags={}):
    """
    :arg within: a stack match as understood by
        :func:`loopy.context_matching.parse_stack_match`.
    """

    # {{{ normalize arguments, find unique new_inames

    if isinstance(inames, str):
        inames = [iname.strip() for iname in inames.split(",")]

    if isinstance(new_inames, str):
        new_inames = [iname.strip() for iname in new_inames.split(",")]

    from loopy.context_matching import parse_stack_match
    within = parse_stack_match(within)

    if new_inames is None:
        new_inames = [None] * len(inames)

    if len(new_inames) != len(inames):
        raise ValueError("new_inames must have the same number of entries as inames")

    name_gen = knl.get_var_name_generator()

    for i, iname in enumerate(inames):
        new_iname = new_inames[i]

        if new_iname is None:
            new_iname = iname

            if suffix is not None:
                new_iname += suffix

            new_iname = name_gen(new_iname)

        else:
            if name_gen.is_name_conflicting(new_iname):
                raise ValueError("new iname '%s' conflicts with existing names"
                        % new_iname)

            name_gen.add_name(new_iname)

        new_inames[i] = new_iname

    # }}}

    # {{{ duplicate the inames

    for old_iname, new_iname in zip(inames, new_inames):
        from loopy.kernel.tools import DomainChanger
        domch = DomainChanger(knl, frozenset([old_iname]))

        from loopy.isl_helpers import duplicate_axes
        knl = knl.copy(
                domains=domch.get_domains_with(
                    duplicate_axes(domch.domain, [old_iname], [new_iname])))

    # }}}

    # {{{ change the inames in the code

    rule_mapping_context = SubstitutionRuleMappingContext(
            knl.substitutions, name_gen)
    indup = _InameDuplicator(rule_mapping_context,
            old_to_new=dict(list(zip(inames, new_inames))),
            within=within)

    knl = rule_mapping_context.finish_kernel(
            indup.map_kernel(knl))

    # }}}

    # {{{ realize tags

    for old_iname, new_iname in zip(inames, new_inames):
        new_tag = tags.get(old_iname)
        if new_tag is not None:
            knl = tag_inames(knl, {new_iname: new_tag})

    # }}}

    return knl

# }}}


# {{{ rename_inames

def rename_iname(knl, old_iname, new_iname, existing_ok=False, within=None):
    """
    :arg within: a stack match as understood by
        :func:`loopy.context_matching.parse_stack_match`.
    :arg existing_ok: execute even if *new_iname* already exists
    """

    var_name_gen = knl.get_var_name_generator()

    does_exist = var_name_gen.is_name_conflicting(new_iname)

    if does_exist and not existing_ok:
        raise ValueError("iname '%s' conflicts with an existing identifier"
                "--cannot rename" % new_iname)

    if does_exist:
        # {{{ check that the domains match up

        dom = knl.get_inames_domain(frozenset((old_iname, new_iname)))

        var_dict = dom.get_var_dict()
        _, old_idx = var_dict[old_iname]
        _, new_idx = var_dict[new_iname]

        par_idx = dom.dim(dim_type.param)
        dom_old = dom.move_dims(
                dim_type.param, par_idx, dim_type.set, old_idx, 1)
        dom_old = dom_old.move_dims(
                dim_type.set, dom_old.dim(dim_type.set), dim_type.param, par_idx, 1)
        dom_old = dom_old.project_out(
                dim_type.set, new_idx if new_idx < old_idx else new_idx - 1, 1)

        par_idx = dom.dim(dim_type.param)
        dom_new = dom.move_dims(
                dim_type.param, par_idx, dim_type.set, new_idx, 1)
        dom_new = dom_new.move_dims(
                dim_type.set, dom_new.dim(dim_type.set), dim_type.param, par_idx, 1)
        dom_new = dom_new.project_out(
                dim_type.set, old_idx if old_idx < new_idx else old_idx - 1, 1)

        if not (dom_old <= dom_new and dom_new <= dom_old):
            raise LoopyError(
                    "inames {old} and {new} do not iterate over the same domain"
                    .format(old=old_iname, new=new_iname))

        # }}}

        from pymbolic import var
        subst_dict = {old_iname: var(new_iname)}

        from loopy.context_matching import parse_stack_match
        within = parse_stack_match(within)

        from pymbolic.mapper.substitutor import make_subst_func
        rule_mapping_context = SubstitutionRuleMappingContext(
                knl.substitutions, var_name_gen)
        ijoin = RuleAwareSubstitutionMapper(rule_mapping_context,
                        make_subst_func(subst_dict), within)

        knl = rule_mapping_context.finish_kernel(
                ijoin.map_kernel(knl))

        new_instructions = []
        for insn in knl.instructions:
            if (old_iname in insn.forced_iname_deps
                    and within(knl, insn, ())):
                insn = insn.copy(
                        forced_iname_deps=(
                            (insn.forced_iname_deps - frozenset([old_iname]))
                            | frozenset([new_iname])))

            new_instructions.append(insn)

        knl = knl.copy(instructions=new_instructions)

    else:
        knl = duplicate_inames(
                knl, [old_iname], within=within, new_inames=[new_iname])

    knl = remove_unused_inames(knl, [old_iname])

    return knl

# }}}


# {{{ link inames

def link_inames(knl, inames, new_iname, within=None, tag=None):
    # {{{ normalize arguments

    if isinstance(inames, str):
        inames = inames.split(",")

    var_name_gen = knl.get_var_name_generator()
    new_iname = var_name_gen(new_iname)

    # }}}

    # {{{ ensure that each iname is used at most once in each instruction

    inames_set = set(inames)

    if 0:
        # FIXME!
        for insn in knl.instructions:
            insn_inames = knl.insn_inames(insn.id) | insn.reduction_inames()

            if len(insn_inames & inames_set) > 1:
                raise LoopyError("To-be-linked inames '%s' are used in "
                        "instruction '%s'. No more than one such iname can "
                        "be used in one instruction."
                        % (", ".join(insn_inames & inames_set), insn.id))

    # }}}

    from loopy.kernel.tools import DomainChanger
    domch = DomainChanger(knl, tuple(inames))

    # {{{ ensure that projections are identical

    unrelated_dom_inames = list(
            set(domch.domain.get_var_names(dim_type.set))
            - inames_set)

    domain = domch.domain

    # move all inames to be linked to end to prevent shuffly confusion
    for iname in inames:
        dt, index = domain.get_var_dict()[iname]
        assert dt == dim_type.set

        # move to tail of param dim_type
        domain = domain.move_dims(
                    dim_type.param, domain.dim(dim_type.param),
                    dt, index, 1)
        # move to tail of set dim_type
        domain = domain.move_dims(
                    dim_type.set, domain.dim(dim_type.set),
                    dim_type.param, domain.dim(dim_type.param)-1, 1)

    projections = [
            domch.domain.project_out_except(
                unrelated_dom_inames + [iname], [dim_type.set])
            for iname in inames]

    all_equal = True
    first_proj = projections[0]
    for proj in projections[1:]:
        all_equal = all_equal and (proj <= first_proj and first_proj <= proj)

    if not all_equal:
        raise LoopyError("Inames cannot be linked because their domain "
                "constraints are not the same.")

    del domain  # messed up for testing, do not use

    # }}}

    # change the domain
    from loopy.isl_helpers import duplicate_axes
    knl = knl.copy(
            domains=domch.get_domains_with(
                duplicate_axes(domch.domain, [inames[0]], [new_iname])))

    # {{{ change the code

    from pymbolic import var
    subst_dict = dict((iname, var(new_iname)) for iname in inames)

    from loopy.context_matching import parse_stack_match
    within = parse_stack_match(within)

    from pymbolic.mapper.substitutor import make_subst_func
    rule_mapping_context = SubstitutionRuleMappingContext(
            knl.substitutions, var_name_gen)
    ijoin = RuleAwareSubstitutionMapper(rule_mapping_context,
                    make_subst_func(subst_dict), within)

    knl = rule_mapping_context.finish_kernel(
            ijoin.map_kernel(knl))

    # }}}

    knl = remove_unused_inames(knl, inames)

    if tag is not None:
        knl = tag_inames(knl, {new_iname: tag})

    return knl

# }}}


# {{{ remove unused inames

def remove_unused_inames(knl, inames=None):
    """Delete those among *inames* that are unused, i.e. project them
    out of the domain. If these inames pose implicit restrictions on
    other inames, these restrictions will persist as existentially
    quantified variables.

    :arg inames: may be an iterable of inames or a string of comma-separated inames.
    """

    # {{{ normalize arguments

    if inames is None:
        inames = knl.all_inames()
    elif isinstance(inames, str):
        inames = inames.split(",")

    # }}}

    # {{{ check which inames are unused

    inames = set(inames)
    used_inames = set()
    for insn in knl.instructions:
        used_inames.update(knl.insn_inames(insn.id))

    unused_inames = inames - used_inames

    # }}}

    # {{{ remove them

    from loopy.kernel.tools import DomainChanger

    for iname in unused_inames:
        domch = DomainChanger(knl, (iname,))

        dom = domch.domain
        dt, idx = dom.get_var_dict()[iname]
        dom = dom.project_out(dt, idx, 1)

        knl = knl.copy(domains=domch.get_domains_with(dom))

    # }}}

    return knl

# }}}


# {{{ affine map inames

def affine_map_inames(kernel, old_inames, new_inames, equations):
    """Return a new *kernel* where the affine transform
    specified by *equations* has been applied to the inames.

    :arg old_inames: A list of inames to be replaced by affine transforms
        of their values.
        May also be a string of comma-separated inames.

    :arg new_inames: A list of new inames that are not yet used in *kernel*,
        but have their values established in terms of *old_inames* by
        *equations*.
        May also be a string of comma-separated inames.
    :arg equations: A list of equations estabilishing a relationship
        between *old_inames* and *new_inames*. Each equation may be
        a tuple ``(lhs, rhs)`` of expressions or a string, with left and
        right hand side of the equation separated by ``=``.
    """

    # {{{ check and parse arguments

    if isinstance(new_inames, str):
        new_inames = new_inames.split(",")
        new_inames = [iname.strip() for iname in new_inames]
    if isinstance(old_inames, str):
        old_inames = old_inames.split(",")
        old_inames = [iname.strip() for iname in old_inames]
    if isinstance(equations, str):
        equations = [equations]

    import re
    eqn_re = re.compile(r"^([^=]+)=([^=]+)$")

    def parse_equation(eqn):
        if isinstance(eqn, str):
            eqn_match = eqn_re.match(eqn)
            if not eqn_match:
                raise ValueError("invalid equation: %s" % eqn)

            from loopy.symbolic import parse
            lhs = parse(eqn_match.group(1))
            rhs = parse(eqn_match.group(2))
            return (lhs, rhs)
        elif isinstance(eqn, tuple):
            if len(eqn) != 2:
                raise ValueError("unexpected length of equation tuple, "
                        "got %d, should be 2" % len(eqn))
            return eqn
        else:
            raise ValueError("unexpected type of equation"
                    "got %d, should be string or tuple"
                    % type(eqn).__name__)

    equations = [parse_equation(eqn) for eqn in equations]

    all_vars = kernel.all_variable_names()
    for iname in new_inames:
        if iname in all_vars:
            raise LoopyError("new iname '%s' is already used in kernel"
                    % iname)

    for iname in old_inames:
        if iname not in kernel.all_inames():
            raise LoopyError("old iname '%s' not known" % iname)

    # }}}

    # {{{ substitute iname use

    from pymbolic.algorithm import solve_affine_equations_for
    old_inames_to_expr = solve_affine_equations_for(old_inames, equations)

    subst_dict = dict(
            (v.name, expr)
            for v, expr in old_inames_to_expr.items())

    var_name_gen = kernel.get_var_name_generator()

    from pymbolic.mapper.substitutor import make_subst_func
    from loopy.context_matching import parse_stack_match

    rule_mapping_context = SubstitutionRuleMappingContext(
            kernel.substitutions, var_name_gen)
    old_to_new = RuleAwareSubstitutionMapper(rule_mapping_context,
            make_subst_func(subst_dict), within=parse_stack_match(None))

    kernel = (
            rule_mapping_context.finish_kernel(
                old_to_new.map_kernel(kernel))
            .copy(
                applied_iname_rewrites=kernel.applied_iname_rewrites + [subst_dict]
                ))

    # }}}

    # {{{ change domains

    new_inames_set = set(new_inames)
    old_inames_set = set(old_inames)

    new_domains = []
    for idom, dom in enumerate(kernel.domains):
        dom_var_dict = dom.get_var_dict()
        old_iname_overlap = [
                iname
                for iname in old_inames
                if iname in dom_var_dict]

        if not old_iname_overlap:
            new_domains.append(dom)
            continue

        from loopy.symbolic import get_dependencies
        dom_new_inames = set()
        dom_old_inames = set()

        # mapping for new inames to dim_types
        new_iname_dim_types = {}

        dom_equations = []
        for iname in old_iname_overlap:
            for ieqn, (lhs, rhs) in enumerate(equations):
                eqn_deps = get_dependencies(lhs) | get_dependencies(rhs)
                if iname in eqn_deps:
                    dom_new_inames.update(eqn_deps & new_inames_set)
                    dom_old_inames.update(eqn_deps & old_inames_set)

                if dom_old_inames:
                    dom_equations.append((lhs, rhs))

                this_eqn_old_iname_dim_types = set(
                        dom_var_dict[old_iname][0]
                        for old_iname in eqn_deps & old_inames_set)

                if this_eqn_old_iname_dim_types:
                    if len(this_eqn_old_iname_dim_types) > 1:
                        raise ValueError("inames '%s' (from equation %d (0-based)) "
                                "in domain %d (0-based) are not "
                                "of a uniform dim_type"
                                % (", ".join(eqn_deps & old_inames_set), ieqn, idom))

                    this_eqn_new_iname_dim_type, = this_eqn_old_iname_dim_types

                    for new_iname in eqn_deps & new_inames_set:
                        if new_iname in new_iname_dim_types:
                            if (this_eqn_new_iname_dim_type
                                    != new_iname_dim_types[new_iname]):
                                raise ValueError("dim_type disagreement for "
                                        "iname '%s' (from equation %d (0-based)) "
                                        "in domain %d (0-based)"
                                        % (new_iname, ieqn, idom))
                        else:
                            new_iname_dim_types[new_iname] = \
                                    this_eqn_new_iname_dim_type

        if not dom_old_inames <= set(dom_var_dict):
            raise ValueError("domain %d (0-based) does not know about "
                    "all old inames (specifically '%s') needed to define new inames"
                    % (idom, ", ".join(dom_old_inames - set(dom_var_dict))))

        # add inames to domain with correct dim_types
        dom_new_inames = list(dom_new_inames)
        for iname in dom_new_inames:
            dt = new_iname_dim_types[iname]
            iname_idx = dom.dim(dt)
            dom = dom.add_dims(dt, 1)
            dom = dom.set_dim_name(dt, iname_idx, iname)

        # add equations
        from loopy.symbolic import aff_from_expr
        for lhs, rhs in dom_equations:
            dom = dom.add_constraint(
                    isl.Constraint.equality_from_aff(
                        aff_from_expr(dom.space, rhs - lhs)))

        # project out old inames
        for iname in dom_old_inames:
            dt, idx = dom.get_var_dict()[iname]
            dom = dom.project_out(dt, idx, 1)

        new_domains.append(dom)

    # }}}

    return kernel.copy(domains=new_domains)

# }}}


# vim: foldmethod=marker
