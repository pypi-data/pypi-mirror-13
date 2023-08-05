import collections
from . import conTextItem
#import conTextItem
import copy

#from utils import xmlScrub

class tagItem(collections.namedtuple('tagItem',
    ['conTextItem', 'span','scope','foundPhrase','id'])):
    def __unicode__(self):
        return u"""%s: %s"""%(self.id,self.foundPhrase)
    def __lt__(self,other): return self.span[0] < other.span[0]
    def __le__(self,other): return self.span[0] <= other.span[0]
    def __eq__(self,other):
        return (self.span[0] == other.span[0] and
                self.span[1] == other.span[1])
    def __ne__(self,other): return self.span[0] != other.span[0]
    def __gt__(self,other): return self.span[0] >  other.span[0]
    def __ge__(self,other): return self.span[0] >= other.span[0]


def _autoSetScope(rule,span):
    """
    applies the objects own rule and span to modify the object's scope
    Currently only "forward" and "backward" rules are implemented
    """
    if 'forward' in rule:
        return (span[1],-1)
    elif 'backward' in rule:
        return (0,span[0])

def create_tagItem(ci, span, foundPhrase,id):
    return   tagItem(conTextItem = ci,
                     span=span,
                     scope=_autoSetScope(ci.rule,span),
                     foundPhrase=foundPhrase.lower(),
                     id=id)
def limitCategoryScopeForward(obj1,obj2):
    """If obj1 and obj2 are of the same category
    return a copy of obj1 with modified scope
    """

    # If objects are not of the same category then they don't interact
    if not conTextItem.isA(obj1.conTextItem,
                           obj2.conTextItem):
        return copy.copy(obj1)
    if lessthan(obj1,obj2):
        return create_tagItem(obj1.conTextItem,
                            obj1.span,
                            min(obj1.ti.scope[1],obj2.getSpan()[0]),
                            foundPhrase=obj1.foundPhrase,
                            id=obj1.id)
    else:
        return copy.copy(obj1)

def scope_modifiable(obj):
    return bool(obj.conTextItem.rule) and 'terminate' not in obj.conTextItem.rule

def limitCategoryScopeBackward(obj1,obj2):
    """If obj1 and obj2 are of the same category
    modify the scope of
    """
    if not conTextItem.isA(obj1.conTextItem,obj2.conTextItem):
        return copy.copy(obj1)
    if lessthan(obj2, obj1):
        return create_tagItem(obj1.conTextItem,
                            obj1.span,
                            max(obj1.ti.scope[1],obj2.getSpan()[0]),
                            foundPhrase=obj1.foundPhrase,
                            id=obj1.id)


def limitCategoryScopeBidirectional(obj1,obj2):
    """If obj1 and obj2 are of the same category
    modify the scope of
    """
    return limitCategoryScopeBackward(limitCategoryScopeForward(obj1,obj2),obj2)


def limitScope(obj1,obj2):
    """If obj1 and obj2 are of the same category or if obj2 has a rule of
    'terminate', use the span of obj2 to
    update the scope of obj1
    """
    if not scope_modifiable(obj1):
        return copy.copy(obj1)
    if not conTextItem.isA(obj1.conTextItem,obj2.conTextItem):
        return copy.copy(obj1)
    if not conTextItem.test_rule(obj2.conTextItem, 'terminate'):
        return copy.copy(obj1)

    if conTextItem.test_rule(obj1,'forward'):
        return limitCategoryScopeForward(obj1,obj2)
    if conTextItem.test_rule(obj1,'bidirectional'):
        return limitCategoryScopeBidirectional(obj1,obj2)
    if conTextItem.test_rule(obj1,'backward'):
          return limitCategoryScopeBackward(obj1,obj2)

def applyRule(rule, target):
    """applies rule to target. If the start of target lies within
    the scope of rule, then target may be modified by rule"""
    if not scope_modifiable(target):
        return False
    return rule.span[0] <= target.span[0] <= rule.scope[1]

def replaceCategory(obj,oldCategory,newCategory):
    categories = tuple([c if c != oldCategory.lower().strip() else newCategory \
                            for c in obj.conTextItem.categories])
    ci = conTextItem.conTextItem(literal=obj.literal,
                                 category=categories,
                                 re=obj.re,
                                 rule=obj.rule)

    return create_tagItem(ci, obj.span, obj.scope, obj.foundPhrase,obj.id)


def o1_encompasses_o2(obj1,obj2):
    """tests whether obj2 is completely encompassed within obj1
       ??? should we not prune identical span tagItems???"""
    return obj1.span[0] <= obj2.span[0] and obj1.span[1] >= obj2.span[1]



def isA_tag(obj1,obj2):
    try:
        return conTextItem.isA(obj1.conTextItem,obj2.conTextItem.category)
    except AttributeError:
        return conTextItem.isA(obj1.conTextItem, obj2)

def dist(obj1,obj2):
    """returns the minimum distance from the current object and obj.
    Distance is measured as current start to object end or current end to object start"""
    return min(abs(obj1.span[1]-obj2.span[0]),
               abs(obj1.span[0]-obj2.span[1]))

def lessthan(obj1,obj2):
    return obj1.span[1]<obj2.span[0]
def tagItem2string(obj):
    return u"""%s: %s"""%(obj.id,obj.foundPhrase)
