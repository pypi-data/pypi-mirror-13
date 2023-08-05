import time

'''
Aspects are a hierarchical tagging system.
'''

def iterTagDown(tag,div='.'):
    '''
    Yield tags from top to bottom.

    Example:

        iterTagDown('foo.bar.baz') -> ('foo','foo.bar','foo.bar.baz')

    '''
    parts = tag.split(div)
    for i in range(len(parts)):
        yield div.join(parts[0:i+1])

def iterTagUp(tag,div='.'):
    '''
    Yield tags from top to bottom.

    Example:

        iterTagUp('foo.bar.baz') -> ('foo.bar.baz','foo.bar','foo')

    '''
    parts = tag.split(div)
    psize = len(parts)
    for i in range(psize):
        yield div.join( parts[:psize-i] )

def getSubTags(tag,tags):
    '''
    Return a list of tags *below* tag.
    '''
    pref = '%s.' %  tag
    return { p:v for (p,v) in tags.items() if p.startswith(pref) }

def getTufoSubs(tufo, tag):
    form = tufo[1].get('tufo:form')
    pref = '%s:tag:%s.' % (form,tag)
    props = [ '%s:tag:%s' % (form,tag) ]
    props.extend([ p for p in tufo[1].keys() if p.startswith(pref) ])
    return props

def genTufoRows(tufo, tag, valu=None):
    # gen rows for a cortex
    now = int(time.time())
    if valu == None:
        valu = int(time.time())

    iden = tufo[0]
    form = tufo[1].get('tufo:form')
    props = [ '%s:tag:%s' % (form,tag) for tag in iterTagDown(tag) ]
    return [ (iden,prop,valu,now) for prop in props if tufo[1].get(prop) == None ]

def getTufoTags(tufo):
    '''
    Return a dict of tag:val for tags on tufo.

    Example:

        tags = getTufoTags(tufo)

    '''
    pref = '%s:tag:' % tufo[1].get('tufo:form')
    props = [ (p,v) for (p,v) in tufo[1].items() if p.startswith(pref) ]
    return { p.split(':',2)[2]:v for (p,v) in props }
