#!/usr/bin/env python
import string
import re, types

#from pprint import pprint

class Base:
    accepted_params = []

    VAR_SIGN = "%"

    def __init__(self, params = {}):
        """
            Constructor.

            Initializes the object and dynamically creates members according to each derived class
        """
        self.__dict__["Super"] = "Base"
        for p in self.accepted_params:
            self.__dict__[p['name']] = None
            if p['is_required'] and not params.has_key(p['name']):
                raise Exception('Required request parameter',p['name'] ,'is missing')
            if params.has_key(p['name']):
                if p['is_array']:
                    if not (type(params[p['name']]) == type(list())):
                        raise Exception(p['name'],'is not an array')
                    self.__dict__[p['name']] = map (lambda s :p['type'](s) if p.has_key('type') else str(s) if type(s) == unicode else s, params[p['name']])
                else:
                    if p.has_key('type'):
                        self.__dict__[p['name']] = p['type'](params[p['name']])
                    else:
                        self.__dict__[p['name']] = params[p['name']]

    def get_Vars(self):
        expr = self._filterVariables()
        #print expr
        varrs = []
        for ex in expr:
            varrs.extend(self._searchVar(ex))
            #varrs.extend(re.split('(\ )+', ex, flags=re.IGNORECASE))

        return list(set(varrs))

    def _searchVar(self, word):
        allowed = string.letters + string.digits + '_'
        #print word
        varrs = []
        occ_pos = [m.start() for m in re.finditer(self.VAR_SIGN, word)]
        #print occ_pos
        for pos in occ_pos:
            i = 2
            while all(c in allowed for c in word[pos + 1:pos + i + 1]) and i < len(word) - pos  and word[pos + i] != ' ':
                i = i + 1
            varrs.append(word[pos:pos + i])
        return varrs


    def _filterVariables(self):
        varr = []

        for val in self.__dict__.values():
            if type(val) == list:
                for item in val:
                    varr += self._parseItem(item)
            elif type(val) == dict:
                for item in val.values():
                    varr += self._parseItem(item)
            else:
                varr += self._parseItem(val)



        return list(set(varr))

    def _parseItem(self, item):
        if issubclass(item.__class__,Base) or isinstance(item, Base):
            return item._filterVariables()
        elif type(item) == str or type(item) == unicode:
            if self.VAR_SIGN in item:
                return [str(item)]
        return []


    def __str__(self):
        return self.printStr()

    def printStr(self, index = 0):
        """
            pprint of the entire tree
        """
        sep = "  :  "
        i = '\n'+('  '* index)
        s = ""
        for k in self.__dict__:
            if k != "Super":
                s = s + i + k + sep
            if isinstance(self.__dict__[k], Base) or issubclass(self.__dict__[k].__class__,Base) or (isinstance(self.__dict__[k], types.InstanceType) and "Super" in self.__dict__[k].__dict__):
                s = s + self.__dict__[k].printStr(index + 1)
            elif type(self.__dict__[k]) == list:

                ss = ""
                for p in self.__dict__[k]:
                    if isinstance(p, Base) or issubclass(p.__class__,Base) or (isinstance(p, types.InstanceType) and "Super" in p.__dict__):
                        ss = ss + '  ' + p.printStr(index +1)
                    else:
                        if ss != "":
                            ss = ss + ', ' + str(p)
                        else:
                            ss = str(p)
                s = s + "["+ ss + "]"
            elif type(self.__dict__[k]) == dict:
                for p in self.__dict__[k]:
                    if isinstance(self.__dict__[k][p], Base) or issubclass(self.__dict__[k][p].__class__,Base) or (isinstance(self.__dict__[k][p], types.InstanceType) and "Super" in self.__dict__[k][p].__dict__):
                        s = s + i + '  ' + p + sep + self.__dict__[k][p].printStr(index +1)

                    else:
                        s = s + i + '  ' + p + sep +str(self.__dict__[k][p])
            else:
                if k != "Super":
                    s = s + str(self.__dict__[k])

        return s


    def getVariableMap(self):
        """
            Retriving variables whose values must be selected by the system
             Example:
             m = [
                    {
                         "%num_machines" : [1..8], "DiscreteSet" : False
                     }, ...
             ]
        """
        m = []

        for key in self.__dict__:
            item = self.__dict__[key]
            #print item, type(item)
            if isinstance(item, Base) or issubclass(item.__class__,Base) or (isinstance(item, types.InstanceType) and "Super" in item.__dict__):
                m.extend(item.getVariableMap())

            elif type(item) == list:
                for p in item:
                    if isinstance(p, Base) or issubclass(p.__class__,Base) or (isinstance(p, types.InstanceType) and "Super" in p.__dict__):
                        m.extend(p.getVariableMap())

            elif type(item) == dict:
                for p in item.values():
                    if isinstance(p, Base) or issubclass(p.__class__,Base) or (isinstance(p, types.InstanceType) and "Super" in p.__dict__):
                        m.extend(p.getVariableMap())
        #print "Variable map for class ", self.__class__

        return m





