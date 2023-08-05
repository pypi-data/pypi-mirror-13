'''
An API to assist with the creation and enforcement of cortex data models.
'''
import re
import fnmatch
import collections

import synapse.aspects as s_aspects

hexre = re.compile('^[0-9a-z]+$')

class ModelError(Exception):pass

class BadTypeParse(ModelError):
    def __init__(self, name, text):
        self._type_name = name
        self._type_text = text
        mesg = '%s: %r' % (name,text)
        ModelError.__init__(self, mesg)

class BadTypeNorm(BadTypeParse):pass

class NoSuchProp(ModelError):pass
class NoSuchType(ModelError):pass
class NoSuchForm(ModelError):pass

class DupDataType(ModelError):pass
class DupPropName(ModelError):pass

class BadEnumValu(ModelError):
    def __init__(self, enum, valu):
        ModelError.__init__(self, '%s: %s' % (enum, valu))

def propdef(name, **info):
    return (name,info)

class DataType:
    '''
    Base class for the  data types system.
    '''

    def __init__(self):
        pass

    def norm(self, valu):
        '''
        Return a "purified" system mode value from system mode input.
        '''
        return valu

    def repr(self, valu):
        '''
        Return a humon display form from system form.
        '''
        return valu

    def parse(self, text):
        '''
        Parse humon readable input and return system form.
        '''
        return text

class StrType(DataType):
    '''
    Simple sting type with no constraints.
    '''
    pass

class LwrType(DataType):

    def norm(self, valu):
        return valu.lower()

    def parse(self, text):
        return text.lower()

class TagType(DataType):
    '''
    Tag string type which normalizes to lower case.
    '''

    def norm(self, valu):
        return valu.lower()

    def parse(self, text):
        parts = text.lower().split('.')
        return '.'.join( [ p.strip() for p in parts ] )

class IntType(DataType):
    '''
    Simple integer type with no constraints.
    '''
    def repr(self, valu):
        return str(valu)

    def parse(self, text):
        return int(text)

class GuidType(DataType):

    def parse(self, text):
        # FIXME check for valid hex
        return text

class BoolType(DataType):

    def repr(self, valu):
        return str(bool(valu))

    def norm(self, valu):
        return int(valu)

    def parse(self, text):

        ltxt = text.lower()
        if ltxt not in ('true','false','0','1'):
            raise BadTypeParse('bool',text)

        if text.lower() == 'true':
            return 1

        return 0

class EnumType(DataType):

    def __init__(self, name, tags):
        self.name = name
        self.tags = tags

    def norm(self, valu):
        if valu not in self.tags:
            raise BadEnumValu(self.name,valu)
        return valu

    def parse(self, text):
        if text not in self.tags:
            raise BadEnumValu(self.name,text)
        return valu

class HexType(DataType):

    def norm(self, valu):
        valu = valu.lower()
        if not hexre.match(valu):
            raise BadTypeParse('hex', valu)

        return valu

    def parse(self, text):
        text = text.lower()
        if not hexre.match(text):
            raise BadTypeParse('hex', text)

        return text

class HashType(DataType):

    def __init__(self, name, size):
        self._hash_name = name
        self._hash_size = size

    def norm(self, valu):
        valu = valu.lower()
        if not hexre.match(valu):
            raise BadTypeParse(self._hash_name, valu)
        if len(valu) != self._hash_size * 2:
            raise BadTypeNorm(self._hash_name, valu)
        return valu

    def parse(self, text):
        text = text.lower()
        if not hexre.match(text):
            raise BadTypeParse(self._hash_name, text)

        if len(text) != self._hash_size * 2:
            raise BadTypeParse(self._hash_name, text)

        return text

#FIXME TODO
#class TimeType(DataType):
#class Ipv4Type(DataType):
#class Ipv4StrType(DataType):
#class CidrType(DataType):

class DataModel:

    def __init__(self, model=None):

        self.types = {}
        self.model = {}

        if model != None:
            self.model.update(model)

        self.model.setdefault('ver', (0,0,0))

        self.model.setdefault('enums',{})
        self.model.setdefault('tufos',{})
        self.model.setdefault('props',{})
        self.model.setdefault('globs',{})

        self.subs = collections.defaultdict(list)  # prop:subprops
        self.cache = {} # for globs

        self.addDataType('int', IntType())
        self.addDataType('lwr', LwrType())
        self.addDataType('str', StrType())
        self.addDataType('hex', HexType())
        self.addDataType('tag', TagType())
        self.addDataType('bool', BoolType())

        self.addDataType('hash:md5', HashType('hash:md5', 16) )
        self.addDataType('hash:sha1', HashType('hash:sha1', 20) )
        self.addDataType('hash:sha256', HashType('hash:sha256', 32) )
        self.addDataType('hash:sha384', HashType('hash:sha384', 48) )
        self.addDataType('hash:sha512', HashType('hash:sha512', 64) )

        self.addDataType('guid', GuidType())

        for name,tags in self.model.get('enums').items():
            self._loadDataEnum(enum,tags)

        props = self.model.get('props')
        [ self._addSubRefs(pdef) for pdef in props.values() ]

    def getDataVer(self):
        return self.model.get('ver')

    def setDataVer(self, maj, min, rev):
        '''
        Set the data modle version for this data model.

        Example:

            model.setDataVer(1,2,3)

        '''
        self.model['ver'] = (maj, min, rev)

    def _loadDataEnum(self, enum, tags):
        self.addDataType(enum, EnumType(enum,tags))

    def addTufoForm(self, form, **propinfo):
        '''
        Add a tufo form to the data model

        Example:

            # must add tufo before adding tufo props
            model.addTufoForm('woot')

        '''
        propinfo['form'] = True
        self.addPropDef(form, **propinfo)

    def addDataEnum(self, enum, tags):
        '''
        Add an enum data type to the data model.

        Example:

            model.addDataEnum('woot', ('foo','bar','baz','faz') )

        '''
        if self.types.get(enum) != None:
            raise DupDataType(enum)

        enums = self.model.get('enums')
        tags = enums.get(enum)
        if tags != None:
            raise DupDataType(enum)

        enums[enum] = tags
        self._loadDataEnum(enum,tags)

    def addDataType(self, name, typeobj):
        '''
        Add a data type validator/parser to the data model.

        Example:

            class FooType(DataType):
                # over-ride stuff

            model.addDataType('foo', FooType() )

        '''
        if self.types.get(name) != None:
            raise DupDataType(name)
        self.types[name] = typeobj

    def getDataType(self, name):
        '''
        Return the DataType instance for the given type name.

        Example:

            typeobj = model.getDataType('int')

        '''
        return self.types.get(name)

    def getModelDict(self):
        '''
        Return the model dictionary for the current data model.

        Example:

            md = model.getModelDict()

        '''
        return dict(self.model)

    def addTufoProp(self, form, prop, **propinfo):
        '''
        Add a property to the data model.

        Example:

            # all foo tufos must have a foo:bar property
            model.addTufoProp('foo', 'bar', ptype='int', defval=0)

        '''
        pdef = self.getPropDef(form)
        if pdef == None:
            raise NoSuchForm(form)

        propinfo['form'] = form
        fullprop = '%s:%s' % (form,prop)

        self.addPropDef(fullprop, **propinfo)

    def addPropDef(self, prop, **propinfo):
        '''
        Add a property definition to the DataModel.

        Example:

            model.addPropDef('foo:bar', ptype='int', defval=30)

        '''
        pdef = self.getPropDef(prop)
        if pdef != None:
            raise DupPropName(prop)

        propinfo.setdefault('doc',None)
        propinfo.setdefault('uniq',False)
        propinfo.setdefault('ptype',None)
        propinfo.setdefault('title',None)
        propinfo.setdefault('defval',None)

        ptype = propinfo.get('ptype')
        if ptype != None and self.getDataType(ptype) == None:
            raise NoSuchType(ptype)

        pdef = (prop,propinfo)
        self.model.get('props')[ prop ] = pdef

        self._addSubRefs(pdef)

    def _addSubRefs(self, pdef):
        for prop in s_aspects.iterTagUp(pdef[0],div=':'):
            if pdef[0] == prop:
                continue
            self.subs[prop].append(pdef)

    def addTufoGlob(self, form, glob, **propinfo):
        '''
        Add a property to the given tufo form.
        '''
        glob = '%s:%s' % (form,glob)
        propinfo['form'] = form
        return self.addPropGlob(glob, **propinfo)

    def addPropGlob(self, glob, **propinfo):
        '''
        Add a property glob to the data model.
        '''
        self.model['globs'][glob] = propinfo

    def getSubProps(self, prop):
        '''
        Return a list of (name,info) prop defs for all sub props.

        Example:

            for pdef in model.getSubProps('foo:bar'):
                dostuff(pdef)

        '''
        return self.subs.get(prop,())

    def getSubPropDefs(self, prop):
        '''
        Return a dict of defvals for props under prop.
        '''
        ret = {}
        for pdef in self.getSubProps(prop):
            valu = pdef[1].get('defval')
            if valu == None:
                continue

            ret[ pdef[0] ] = valu

        return ret

    def getPropRepr(self, prop, valu):
        '''
        Return the humon readable representation for a property.

        Example:
            valu = tufo[1].get(prop)
            x = model.getPropRepr(prop, valu)

        '''
        typeobj = self._getPropTypeObj(prop)
        if typeobj == None:
            return repr(valu)

        return typeobj.repr(valu)

    def _getPropTypeObj(self, prop):
        ptype = self.getPropType(prop)
        if ptype == None:
            return None

        typeobj = self.getDataType(ptype)
        if typeobj != None:
            return typeobj

    def getPropNorm(self, prop, valu):
        '''
        Return a normalized system mode value for the given property.

        Example:

            valu = model.getPropNorm(prop,valu)

        '''
        typeobj = self._getPropTypeObj(prop)
        if typeobj == None:
            return valu

        return typeobj.norm(valu)

    def getNormProps(self, props):
        return { p:self.getPropNorm(p,v) for (p,v) in props.items() }

    def getPropParse(self, prop, valu):
        '''
        Parse a humon input string into a system mode property value.

        Example:

            valu = model.getPropParse(prop, text)

        '''
        typeobj = self._getPropTypeObj(prop)
        if typeobj == None:
            return valu

        return typeobj.parse(valu)

    def getParseProps(self, props):
        return { p:self.getPropParse(p,v) for (p,v) in props.items() }

    def getPropDef(self, prop, glob=True):
        '''
        Return a property definition tufo by property name.

        Example:

            pdef = model.getPropDef('foo:bar')

        '''
        props = self.model.get('props')
        pdef = props.get(prop)
        if pdef != None:
            return pdef

        if not glob:
            return None

        # check the cache
        pdef = self.cache.get(prop)
        if pdef != None:
            return pdef

        # no match, lets check the globs...
        for glob,pinfo in self.model.get('globs').items():
            if fnmatch.fnmatch(prop,glob):
                pdef = (prop,dict(pinfo))
                self.cache[prop] = pdef
                return pdef

    def getPropType(self, prop):
        '''
        Return the name of the data model type for the given property.

        Example:

            ptype = model.getPropType('foo:bar')

        '''
        pdef = self.getPropDef(prop)
        if pdef == None:
            return None

        return pdef[1].get('ptype')

    def getPropDefval(self, prop):
        '''
        Retrieve the default value ( if specified ) for the prop.

        Example:

            defval = model.getPropDefval('foo:bar')

        '''
        pdef = self.getPropDef(prop)
        return pdef[1].get('defval')
