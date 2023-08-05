
import re
from collections import namedtuple, deque
from itertools import chain

from xigt import (XigtCorpus, Meta, MetaChild, ref)
from xigt.errors import XigtError

# XigtPath Grammar
#
# Expr :=
# AbsoluteLocationPath := '/' LocationPath
# LocationPath = Step | LocationPath '/' Step
# Step := Node Predicate*
# Node := Axis NodeTest | AbbreviatedNode
# Axis := AxisName '::' | AbbreviatedAxis
# AxisName := 'self'
#           | 'parent'
#           | 'child'
#           | 'descendant-or-self'
#           | 'attribute'
# AbbreviatedAxis := '' | '//' | '@'
# AbbreviatedNode := '.' | '..'
# NodeTest := NodeName | Function
# Function := FunctionName '(' FunctionParams ')'
# FunctionName := 'referent'
#               | 'referrer'



class XigtPathError(XigtError): pass

xp_tokenizer_re = re.compile(
    r'"(?:\\.|[^\\"])*"|'  # double-quoted strings (allow escaped quotes \")
    r'//?|'  # // descendant-or-self or / descendant
    r'\.\.?|'  # .. parent or . self axes
    #r'::|'  # axis separator
    r'@|'  # attribute axis
    r'\[|\]|'  # predicate
    r'\(|\)|'  # groups
    r'\||'  # union
    r'!=|=|'  # comparisons
    r'(?:text|value|referent|referrer)|'
    r'\*|[^.\/\[\]!=|()]+'  # .., *, igt, tier, item, etc.
)

def tokenize(path):
    return [t.strip() for t in xp_tokenizer_re.findall(path) if t.strip()]

def find(obj, path):
    return next(iterfind(obj, path), None)

def findall(obj, path):
    return list(iterfind(obj, path))

def iterfind(obj, path):
    if path.endswith('/'):
        raise XigtPathError('XigtPaths cannot end with "/"')
    steps = deque(tokenize(path))
    if not steps:
        return
    results = _expr([obj], steps)
    if steps:
        pass  # why is this not working?
        # raise XigtPathError(
        #     'Unexpected termination at {} of invalid path {}'
        #     .format(''.join(steps), path)
        # )
    for result in results:
        yield result

def _expr(objs, steps):
    if steps[0] == '(':
        steps.popleft()
        results = _disjunction(objs, steps)
    elif steps[0] in ('/', '//'):
        if steps[0] == '/':
            steps.popleft()
        results = _step([_get_corpus(objs[0])], steps)
    else:
        results = _step(objs, steps)
    for result in results:
        yield result

def _disjunction(objs, steps):
    results = []
    # NOTE: on the first pass, steps is the original deque, so it is
    #       modified in-place. Afterwards, the copy is reused.
    orig_steps = deque(steps)
    for obj in objs:
        while True:
            results.extend(r for r in _expr([obj], steps))
            next_ = steps.popleft()
            if next_ == '|':
                continue
            elif next_ == ')':
                break
            else:
                raise XigtPathError(
                    'expected "|" or ")": {}'.format(''.join(steps))
                )
        steps = deque(orig_steps)
    # don't yield here; lazy eval screws up the steps deque
    return results

def _step(objs, steps):
    if not steps:
        for obj in objs:
            yield obj
    else:
        step = steps.popleft()
        # axis and nodetests
        if step == '(':
            results = _disjunction(objs, steps)
        elif step == '//':
            name = steps.popleft()
            results = (d for obj in objs
                         for d in _find_descendant_or_self(obj, name))
        elif step == '@':
            attr = steps.popleft()
            results = (res for obj in objs for res in _find_attr(obj, attr))
        elif step == '..':
            results = (obj._parent for obj in objs)
        elif step == '.':
            results = objs
        # elif steps and steps[0] == '::':

        elif step in ('text', 'value', 'referent', 'referrer'):
            steps.popleft()  # (
            args = []
            while steps and steps[0] != ')':
                args.append(steps.popleft())
            steps.popleft()  # )
            results = (r for obj in objs for r in _function(obj, step, args))
        else:
            results = (res for obj in objs for res in _find_child(obj, step))
        # predicates
        while steps and steps[0] == '[':
            predtest = _make_predicate_test(steps)
            results = filter(predtest, results)
        if steps and steps[0] in ('/', '//'):
                if steps[0] == '/':
                    steps.popleft()
                results = _step(results, steps)
        for obj in results:
            yield obj

def _function(obj, func, args):
    # function children
    if func == 'text':
        results = [obj.text]  # ignore args?
    elif func == 'value':
        results = [obj.value()]  # ignore args?
    elif func in ('referent', 'referrer'):
        find_refs = _find_referent if func == 'referent' else _find_referrer
        refattrs = None
        if args:
            refattrs = [ra.strip('"') for ra in args if ra != ',']
        results = find_refs(obj, refattrs)
    for result in results:
        yield result

def _find_child(obj, name):
    results = []
    # node children
    kwargs = {}
    if ':' in name:
        namespace, name = name.split(':', 1)
        kwargs['namespace'] = namespace
    # simple case
    if name == '*' and hasattr(obj, '__iter__'):
        results = list(getattr(obj, 'metadata', []))
        results.extend(obj.select(**kwargs))
    elif (name == 'igt' and hasattr(obj, 'igts') or
          name == 'tier' and hasattr(obj, 'tiers') or
          name == 'item' and hasattr(obj, 'items') or
          name == 'meta' and hasattr(obj, 'metas')):
        # select should just work on the containers as normal
        results = obj.select(**kwargs)
    elif name == 'metadata' and hasattr(obj, 'metadata'):
        # for metadata we need to filter by namespace ourselves (but
        # we don't really expect for <metadata> elements to have a
        # namespace, so maybe this is unnecessary?)
        results = iter(obj.metadata)
        if 'namespace' in kwargs:
            results = filter(
                lambda x: getattr(x, 'namespace', None) == namespace,
                results
            )
    elif isinstance(obj, (Meta, MetaChild)):
        # for MetaChild objects, we need to give the name as well
        kwargs['name'] = name
        results = obj.select(**kwargs)
    for res in results:
        yield res

def _find_attr(obj, attr):
    vals = []
    # pseudo-attributes (members in the model, attrs in the xml and path)
    if attr in ('type', 'id', 'name'):
        val = getattr(obj, attr, None)
        if val is not None:
            vals.append(val)
    else:
        namespace = None
        if ':' in attr:
            namespace, attr = attr.split(':', 1)
        if attr == '*':
            vals.extend(obj.get_attribute(attrkey, namespace=namespace)
                        for attrkey in obj.attributes)
        else:
            vals.append(obj.get_attribute(attr, namespace=namespace))
    for val in vals:
        yield val

def _find_descendant_or_self(obj, name):
    namespace = None
    if ':' in name:
        namespace, name = name.split(':', 1)
    if isinstance(obj, MetaChild):
        objname = obj.name
    else:
        objname = obj.__class__.__name__.lower()
    if (namespace is None or obj.namespace == namespace) and objname == name:
        yield obj
    for child in _find_child(obj, '*'):
        for desc in _find_descendant_or_self(child, name):
            yield desc

def _find_referent(obj, refattrs):
    refs = []
    igt = obj.igt if hasattr(obj, 'igt') else obj
    refd = ref.referents(igt, obj.id, refattrs=refattrs)
    # sort for now because ref.referents doesn't return document order
    for ra, ids in sorted(refd.items()):
        refs.extend(igt.get_any(_id) for _id in ids)
    return refs

def _find_referrer(obj, refattrs):
    refs = []
    igt = obj.igt if hasattr(obj, 'igt') else obj
    refd = ref.referrers(igt, obj.id, refattrs=refattrs)
    # sort for now because ref.referents doesn't return document order
    for ra, ids in sorted(refd.items()):
        refs.extend(igt.get_any(_id) for _id in ids)
    return refs

def _make_predicate_test(steps):
    steps.popleft()  # '['
    # parse expr here?
    subpath = deque()
    while steps[0] not in (']', '=', '!='):
        subpath.append(steps.popleft())
    subpath = ''.join(subpath)  # ugly hack so findall() works
    if steps[0] == ']':
        predtest = lambda obj: any(bool(findall(obj, subpath)))
    elif steps[0] in ('=', '!='):
        cmp = steps.popleft()
        val = steps.popleft().strip('"')
        if cmp == '=':
            predtest = lambda obj: any(v==val for v in findall(obj, subpath))
        elif cmp == '!=':
            predtest = lambda obj: all(v!=val for v in findall(obj, subpath))
    steps.popleft()  # ']'
    return predtest

def _get_corpus(obj):
    while not isinstance(obj, XigtCorpus):
        obj = obj._parent
    return obj
