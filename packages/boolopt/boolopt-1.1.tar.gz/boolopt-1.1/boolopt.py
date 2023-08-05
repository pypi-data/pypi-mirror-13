"""
boolopt

Version 1.1

Copyright 2006 (c) Michael Greenberg.  NewBSD license, listed below.

This module optimizes propositional logic ("boolean expressions", in
programming language terms).  Given an AST in the form of tagged
tuples, it produces an equivalent disjunctive-normal formula that is
minimal.

For the curious and bored, it uses the Quine-McCluskey algorithm.
"""

__license__ = """
/* LICENSE (New BSD)
Copyright (c) 2006, Michael Greenberg.  All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

        1. Redistributions of source code must retain the above copyright notice,
        this list of conditions and the following disclaimer.

        2. Redistributions in binary form must reproduce the above copyright notice,
        this list of conditions and the following disclaimer in the documentation
        and/or other materials provided with the distribution.

        3. The name of Michael Greenberg may not be used to endorse or promote products
        derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

*/


"""

# for 2.2 -- a minimal definition
try:
    from sets import Set
except:
    class Set(list):
        def __or__(self, other):
            s = Set(self)

            for v in other:
                s.add(v)

            return s
        
        def add(self, v):
            if v not in self:
                self.append(v)
        
class Functor:
    """

    The functor pattern.  Defines a class which is really a
    process/function call.

    Implements callable.  When called, it first calls
    functor_called(self, *args) with any arguments passed in.  It then
    calls the functor method (passed into __init__(self, functor))
    with *args, returning the result through functor_return(self,
    *args).

    """
    
    def __init__(self, functor):
        """

        Initializes the functor method.  Will be called when an
        instance is invoked.

        """
        
        self.functor = functor
    
    def __call__(self, *args):
        """

        Makes the class callable.  First calls functor_called(self,
        *args), and then returns the result of functor_return(self,
        *args) applied to the functor given in __init__(self,
        functor).

        """
        
        self.functor_called(*args)
        return self.functor_return(self.functor(*args))

    def functor_called(self, *args):
        """

        Called before the functor method is called.  The default is to
        do nothing.

        """
        
        pass

    def functor_return(self, ret):
        """

        Called with the result of the functor method.  The default is
        to return what was given to it.

        """

        return ret

class Pipeline(Functor):
    """

    A pipeline of functors.  It executes each in turn, passing the
    result of one to the next.

    This pipeline is currently limited to single-argument call/return
    functors, but won't complain if you layer a tuple-passing scheme
    on top.

    """
    
    def __init__(self, *pipeline):
        """

        Sets up the pipeline.  The arguments to this function should
        be Functor instances (though any callable will work), in the
        order they are to be called.  For example:

        p = Pipeline(Add(1), Multiply(2), Pack(HEX))

        Will create a composite functor which will add 1, multiply by
        2, and then pack the number into hexadecimal.

        """
        
        self.pipeline = pipeline
        self.functor  = self.run_pipeline

    def run_pipeline(self, args):
        """

        Runs the pipeline, passing the result from one functor to the
        next until no more remain.

        """
        
        for functor in self.pipeline:
            args = functor(args)

        return args

class RevisitNode(Exception):
    """

    Thrown by a transformation method to indicate that the given node
    should be revisited.  If a node is specified, that node will be
    revisited rather than the original AST node.

    """
    
    def __init__(self, node = None):
        """

        Optional arguments:

            node (AST, default None)
                a different AST to retraverse

        """

        self.node = node

class ASTWalker(Functor):
    """
    
    An AST transformer/visitor, where ASTs are modeled as tuples, in
    which the first element declares the node type, e.g. ('null') or
    ('add', 1, 2).  Follows the functor pattern, where the functor
    function is walk(self, ast).

    Methods can be defined to match specific node types and perform
    actions on them.  The two basic user actions are 'visit' and
    'transform'.  To write a method that counts all nodes of type 't'
    (e.g. ('t', ...)) and leaves all others alone, the class would be
    defined as such:

    class TCounter(ASTWalker):
        def functor_called(self, ast):     self.ts = 0
        def functor_return(self, ast):     return self.ts
        def visit_t(self, node, children): self.ts += 1

    Usage:
    >>> tc = TCounter()
    >>> ts = tc(ast) # ast is bound to some ast

    functor_called is defined so that the functor may be used more
    than once and each time a new count is generated.  functor_return
    is defined so that that tc(ast) returns the count of ts.  The
    visit function is defined so that only AST nodes of type t get
    counted.

    Note that the visit method didn't return anything.  Visit methods
    are purely side-effect based -- they record qualities of the tree.
    To generate new ASTs, you must use transformer actions.  Here is a
    simple functor to change nodes of type 'add' to nodes of type
    'unsigned_add'.

    class UnsignedAdds(ASTWalker):
        def transform_add(self, node, children):
            return tuple(['unsigned_add'] + children)

    Firstly, the functor_ methods are not included.  functor_called
    isn't included because its default is to do nothing, and nothing
    needs to be done.  functor_return isn't included because the
    default is to return the given AST with any transformations made
    on it, which is precisely what is required.

    For a more complicated example, see WFFtoDNF, which converts
    positive-normal formulae into disjunctive-normal formulae.
    
    """

    def __init__(self, **kw):
        """

        Keywords:

            override (dict node-type -> node-type)
              override[k] = v causes method lookup to pretend that AST
              nodes of type k are really of type v

            auto_recur (boolean, default True)
               auto_recur = True causes recursion to happen
               automatically; children passed into node actions will
               have already been processed

        """

        Functor.__init__(self, self.walk)
        self.override   = kw.get('override', {})
        self.auto_recur = kw.get('auto_recur', True)

    def __resolve_method(self, action, node):
        """

        Action-based method resolution.  The two actions are 'visit'
        for non-returning visitors, and 'transform' for AST
        transformations.

        If the node type is overridden (override[k] = v), then
        'action_v' is called.  If the node type is not overridden,
        then 'action_t' is returned.

        If none of these actions exist, then 'action_node' is
        returned.

        If 'action_node' cannot be found, an AttributeError is raised.

        """

        try:
            return getattr(self, action + '_' + self.override.get(node, node))
        except AttributeError:
            return getattr(self, action + '_node')

    def __invoke_method(self, action, ast):
        """
        
        Invokes the appropriate method for recursion.

        If the AST isn't a tuple with a string as its first element,
        then 'action_leaf(self, ast)' is called.  If this does not
        exist, 'leaf(self, ast)' is called.

        If the AST is well-formed, then lookup is performed with
        __resolve_method(self, action, node), where node = ast[0].
        The resolved method is then called with node as its first
        argument and the result of recursion, if auto_recur is set,
        (with self.walk(self, ast)) on the children as its second,
        e.g.  resolved_method(self, node, children).  If the method
        could not be resolved (i.e., neither a specific nor a default
        method exists), node(self, type, children) is called.

        """

        try:
            if type(ast) != tuple or \
                   len(ast) == 0 or \
                   type(ast[0]) != str:
                return getattr(self, action + '_leaf')(ast)
        except AttributeError:
            return self.leaf(ast)

        try:
            node     = ast[0]
            children = list(ast[1:])
            
            return self.__resolve_method(action, node)(node, children)
        except AttributeError:
            return self.node(node, children)

    def __auto_recur(self, ast):
        """

        Performs recursion (if it is specified to occur
        automatically).  It calls walk(self, ast) on each child of the
        AST, or simply returns the AST if it is not well-formed.

        """
        
        if not self.auto_recur or \
               type(ast) != tuple or \
               len(ast) == 0 or type(ast[0]) != str:
            return ast

        return tuple([ast[0]] + map(self.walk, ast[1:]))
            
    def walk(self, ast):
        """

        Walks the AST.  If recursion is set to occur automatically,
        first the child nodes are recurred on.  All visitation and
        transformation will work on the recursive result.

        Then the visitor method is looked up and invoked with
        __invoke_method(self, action, ast).  If the visitor method
        returns anything other than None, transformation will not
        occur.

        Then the transformer method is looked up and similarly
        invoked.  The transformer may either return nothing (in which
        case the original AST is returned), return a new AST, or throw
        a 'RevisitNode' exception (defined above) with a new node
        listed.  This node will then be walked.

        """
        
        ast = self.__auto_recur(ast)
        
        # call visitor methods
        aborting = self.__invoke_method('visit', ast)
        if aborting is not None: return ast

        # call transformer methods
        try:
            transformed = self.__invoke_method('transform', ast)
        except RevisitNode, revisit:
            return self.walk(revisit.node or ast)

        return transformed or ast

    def leaf(self, ast):
        pass

    def node(self, node, children):
        pass


class PLFtoWFF(ASTWalker):
    """

    Transforms a propositional logic formula (PLF) to a well-formed
    formula (WFF).  A WFF is a propositional logic formula where
    negation is applied only to propositions and the only boolean
    operations performed are conjunction and inclusive disjunction.
    (For those of you who are into that kind of thing, this is called
    positive-normal form.)

    It does this by reducing negations and eliminating the asymmetric
    difference and exclusive disjunction operators.

    """

    def __init__(self, **kw):
        kw.setdefault('override', {})
        kw['override']['nand'] = 'demorgan'
        kw['override']['nor']  = 'demorgan'
        kw['auto_recur'] = True
        ASTWalker.__init__(self, **kw)

    def transform_minus(self, node, children):
        not_branch = self.walk(('not', children[1]))

        return ('and', children[0], not_branch)

    def transform_demorgan(self, node, children):
        deMorgan = { 'and': 'or',  'or': 'and',
                    'nand': 'or', 'nor': 'and' }
    
        notl = self.walk(('not', children[0]))
        notr = self.walk(('not', children[1]))

        return (deMorgan.get(node), notl, notr)
    
    def transform_xor(self, node, children):
        l    = children[0]
        r    = children[1]
        notl = self.walk(('not', l))
        notr = self.walk(('not', r))

        return ('or', ('and', l, notr), ('and', notl, r))

    def transform_not(self, node, children):
        child = children[0]
        ctype = child[0]

        if   ctype == 'not':     return child[1]
        elif ctype == 'prop':    return ('notprop', child[1])
        elif ctype == 'notprop': return ('prop', child[1])
        elif ctype in ['and', 'or']:
            return self.transform_demorgan(child[0], child[1:])

class WFFtoDNF(ASTWalker):
    """

    Translates a well-formed formula in positive-normal form into a
    disjunctive-normal form.  This is represented as a list of lists
    of tuples, where the tuple values are of the form:

    ('prop', _) and ('notprop', _)

    A list of tuples represents a conjunction; the DNF formula is the
    disjunction of each of these conjunctions.

    For example:

    ('or', ('and', ('prop', 'a'), ('notprop', 'b')),
           ('and', ('notprop', 'a'), ('prop', 'b')))

    The exclusive-or operator, will turn into:    

    [[('prop', 'a'), ('notprop', 'b')], [('notprop', 'a'), ('prop', 'b')]]

    """

    def __init__(self):
        ASTWalker.__init__(self, auto_recur = 'True')
    
    def functor_called(self, ast): self.props = Set()
    def functor_return(self, dnf): return self.clean(dnf)

    def clean(self, p):
        """

        Cleans a DNF.  It drops duplicate propositions in
        conjunctions, contradictory conjunctions, and duplicate
        conjunction clauses.

        """

        new_p = []

        for conj in p:
            s = []

            contradiction = 0
            for t in conj:
                # stop when we find a contradiction
                if (t[0] == 'prop' and ('notprop', t[1]) in s) or \
                   (t[0] == 'notprop' and ('prop', t[1]) in s):
                    contradiction = 1
                    break
                
                # don't include duplicates, but go on
                if t in s:
                    continue
                s.insert(len(s), t)

            if not contradiction:
                if s not in new_p:
                    new_p.insert(len(new_p), s)

        return new_p

    def visit_prop(self, node, children):
        self.props.add(children[0])

    def visit_notprop(self, node, children):
        self.props.add(children[0])

    def transform_node(self, node, children):
        return [[tuple([node] + children)]]

    def transform_or(self, node, children):
        return children[0] + children[1]

    def transform_and(self, node, children):
        j = []
        for lp in children[0]:
            for rp in children[1]:
                j.append(lp + rp)

        return j

class DNFtoWFF(Functor):
    """

    Converts a disjunctive-normal form formula into a positive-
    normal form AST (a WFF).  The result is a chain of or nodes,
    with the left branch leading to a chain of and nodes.

    For example:

    [[('prop', 'a'), ('notprop', 'b')], [('notprop', 'a'), ('prop', 'b')]]

    This is the familiar exclusive-or operator.  It would result in:

    ('or', ('and', ('prop', 'a'), ('notprop', 'b'))
           ('and', ('notprop', 'a'), ('prop', 'b')))

    """
    
    def __init__(self):
        Functor.__init__(self, self.convert_disjunction)

    def convert_disjunction(self, dnf):
        if len(dnf) == 1:
            return self.convert_conjunction(dnf[0])
        else:
            return ('or', \
                    self.convert_conjunction(dnf[0]), \
                    self.convert_disjunction(dnf[1:]))

    def convert_conjunction(self, cnf):
        if len(cnf) == 1:
            return cnf[0]
        else:
            return ('and', \
                    cnf[0], \
                    self.convert_conjunction(cnf[1:]))

class PropSet(ASTWalker):
    def __init__(self):
        ASTWalker.__init__(self, auto_recur = True)
    
    def functor_called(self, ast): self.props = Set()
    def functor_return(self, ast): return self.props
    def visit_prop(self, node, children): self.props.add(children[0])
    def visit_notprop(self, node, children): self.props.add(children[0])
         
class QuineMcCluskey(Functor):
    """

    Functor class to minimize DNF formulae.  Takes in a logic formula
    (using and, or, not, nor, nand, and xor) and produces the DNF
    minterm.

    The DNF passed in MUST NOT have duplicates (at the conjunction or
    disjunction level) or contradictions (at the conjunction level).

    """

    T = '1' # true
    F = '0' # false
    D = '-' # don't care

    def __init__(self, propsource = lambda dnf: None):
        """

        Initializes the functor.  If propsource is set, it will be
        called with the DNF formula with which the functor is invoked.
        It should return a list of propositions appearing in the
        formula.

        """
        
        Functor.__init__(self, self.reduce)
        self.propsource = propsource

    def reduce(self, dnf):
        """

        Performs Quine-McCluskey reduction.  The original tables are
        in the tables field; the prime implicants are in the primes
        field.

        """

        self.dnf = dnf
        props = self.propsource(self.dnf) or self.get_props(self.dnf)
        
        self.columns = list(props)
        self.columns.sort()
        self.table   = self.arrange(self.columns, self.dnf)
        self.primes  = self.find_prime_implicants(self.table, self.columns)
        self.exps    = self.expand(self.primes)
        self.cover   = self.determine_cover(self.exps)
        return self.to_dnf(self.cover, self.columns)

    def get_props(self, dnf):
        """

        Get the set of properties in a given DNF-formula.

        """

        props = Set()
        
        for conj in dnf:
            for term in conj:
                props.add(term[1])

        return list(props)

    def arrange(self, columns, dnf):
        """
        
        Arranges a disjunctive-normal formula into a set of minterms
        (binary string table).

        """

        table = []

        for conj in dnf:
            row = []
            for column in columns:
                if ('prop', column) in conj:      v = self.T
                elif ('notprop', column) in conj: v = self.F
                else:                             v = self.D

                row.insert(len(row), v)
            table.insert(len(table), row)

        return table

    def find_prime_implicants(self, table, columns):
        """

        Determines the prime implicants of a given set of minterms
        (binary string table).

        """

        curr = list(table)

        while 1:
            next, mark = self.__table_pass(curr, columns)

            mark.sort()
            mark.reverse()

            if len(mark):
                for m in mark:
                    del curr[m]
            else:
                return curr

            for r in next:
                if r not in curr:
                    curr.insert(len(curr), r)

    def __table_pass(self, table, columns):
        next = []
        mark = []

        for i in range(0, len(table)):
            r_i = table[i]

            for j in range(0, i):
                r_j = table[j]
                    
                r = self.__reconcile(r_i, r_j, columns)
                if r:
                    if r not in next:
                        next.insert(len(next), r) # add the reduction
                    if j not in mark:
                        mark.insert(len(mark), j) # mark row j as used

        return (next, mark)


    def __reconcile(self, r1, r2, columns):
        diffs = 0

        r = map(lambda x: self.D, columns) # prepare "don't care columns"
        for c in range(0, len(columns)):
            if r1[c] == r2[c]:
                r[c] = r1[c]

            elif diffs == 0:
                # record the difference and leave it as "don't care"
                diffs = 1

            else:
                # tolerate only one difference
                return None

        return r

    def expand(self, primes):
        """
        
        Expands a set of prime implicants into their digital outputs.

        e.g., for columns ABCD, '0-10' expands into ['0010', '0110'],
              which is further translated into [2, 6]

        """

        exps = {}

        for pi in primes:
            exps[''.join(pi)] = map(lambda e: int(''.join(e), 2), \
                                    self.__expansions(pi))

        return exps
            

    def __expansions(self, pi):
        expansions = [[]]

        def add_term(t, exps):
            for e in exps:
                e.insert(len(e), t)

            return exps

        for t in pi:
            if t != self.D:
                expansions = add_term(t, map(list, expansions))
            else:
                expansions = add_term(self.T, map(list, expansions)) + \
                             add_term(self.F, map(list, expansions))

        return expansions

    def determine_cover(self, exps):
        # calculate output set
        outputs = Set()
        for exp in exps.values():
            outputs |= Set(exp)

        # calculate back mapping from outputs to inputs
        backmap = {}
        for o in outputs:
            for e in exps:
                if o in exps[e]:
                    backmap.setdefault(o, list())
                    backmap[o].insert(len(backmap[o]), e)

        epi = []
       
        # FIND ESSENTIAL PRIME IMPLICANTS
        for o in dict(backmap):
            mappers = backmap[o]

            if len(mappers) == 1:
                if mappers[0] not in epi:
                    epi += mappers
                del backmap[o]

        # try to stop here
        if not len(backmap):
            return epi

        # FUTHER REDUCE COVER WITH EPI
        for o in dict(backmap):
            mappers = backmap[o]

            for pi in epi:
                if pi in mappers:
                    del backmap[o]
                    break

        # try again to stop
        if not len(backmap):
            return epi

        # CHOOSE PI TO FINISH COVER
        import random
        
        for mappers in backmap.values():
            for pi in epi:
                if pi not in mappers:
                    epi += [random.choice(mappers)]

        return epi

    def to_dnf(self, cover, columns):
        dnf = []
        
        for epi in cover:
            conj = []
            
            for term, prop in zip(epi, columns):
                if   term == self.T: conj.append(('prop',    prop))
                elif term == self.F: conj.append(('notprop', prop))

            dnf.append(conj)

        return dnf

def optimize(dnf):
    """

    Optimizes a disjunctive-normal form formula, for the OOP-uneasy.
    The DNF passed in MUST NOT have duplicates (at the conjunction or
    disjunction level) or contradictions (at the conjunction level).
    DNF formulae generated from prepositional logic ASTs as described
    above will have this property.

    An unforunate side affect of the Quine-McCluskey system is that x !=
    optimize(x) does not imply that x isn't optimal -- clauses may be
    reordered. One must check per-clause.

    """
    
    return QuineMcCluskey()(dnf)
                                                 
