import re

class AssetParser(object):
    
    def __init__(self):
        self.source = str()

    def __str__(self):
        return self.source

    def __repr__(self):
        return self.source

    def parse(self, source):

        if source:
            self.source = source
        try:
            self.semicolon()
        except:
            raise Exception("Could not parse ';' symbol.")
        try:
            self.colon()
        except:
            raise Exception("Could not parse ':' symbol.")
        try:
            self.at()
        except:
            raise Exception("Could not parse '@'' symbol.")
        try:
            self.square_brackets()
        except:
            raise Exception("Could not parse '..[..]..' square brackets.")
        try:
            self.tilde()
        except:
            raise Exception("Could not parse '~' symbol. ")
        try:
            self.lists()
        except:
            raise Exception("Could not transform lists to dicts.")
        return self.result
    
    def semicolon(self):
        self.result = self.source.split(';')

    def colon(self):
        self.result = [{s.split(':')[0].strip(): 
                        s.split(':')[1].strip()}
                        for s in self.result]

    def at(self):
        for ix, item in enumerate(self.result):
            at = item.values()[0].split('@')
            if len(at) == 1:
                at.append('~')
            elif len(at) == 2:
                pass
            else:
                # raise error
                raise Exception("Malformed string, cannot be more than 1 @ marks in token.")
            if len(at) == 2:
                self.result[ix][item.keys()[0]] = {'units': at[0], 'price': at[1]}

    def square_brackets(self):
        # break leafs into three parts
        for ix, item in enumerate(self.result):
            for key,value in enumerate(item.values()[0]):
                
                s = item.values()[0][value]
                
                # if [ and ] in string, then:
                # 1. what's behind [, is interval,
                # 2. what's after ], is unit,
                # 3. what's between is formula
                if s.count('[')==1 and s.count(']')==1 and s.find(']')>s.find('['):
                    
                    interval = s.split('[')[0]
                    formula = s.split('[')[1].split(']')[0]
                    unit = s.split(']')[1]

                # if [] not in string, then:
                # string is interval with possible letters at the end, indicating units
                else:
                    # find last number in the string
                    p = re.compile('(\d+)(?!.*\d)').search(s)
                    if p:
                        unit = s[p.end():]      # the string after last number
                        interval = s[0:p.end()] # the string before last number
                        formula = ''
                    elif '~' in s:              # no information was given
                        unit = u''
                        interval = u''
                        formula = u''
                    else:
                        raise Exception("No last number or '~' symbol in substring.")
                    
                self.result[ix][item.keys()[0]][value] = [interval, formula, unit]

    def tilde(self):
        for ix, item in enumerate(self.result):
            for key,value in enumerate(item.values()[0]):
                s = item.values()[0][value][0]
                if '~' in s:
                    interval = s.split('~')
                else:
                    interval = [s,s]
                self.result[ix][item.keys()[0]][value][0] = interval

    def lists(self):
        # leafs of 'units' and 'price' to dicts, like
        """
        Example input:
        
        [
        {u'solar cell assemblies': {'price': [[u'5.5', u'5.9'],
         u'beta(2,2)((x-a)/(b-a))',
         u'h'],
        'units': [[u'1', u'2'], u'exp(x)', u'']}}
        ]
        
        Example output:
        [
         {'solar cell assemblies': 
          {
            'min_units': '1',
            'max_units': '2',
            'f_units': 'exp(x)',
            'min_price': '5.5',
            'max_price': '5.9',
            'f_price': 'beta(2,2)((x-a)/(b-a))',
            'price_unit': 'h'
            }
         },
         ...
        ]
        """
        for ix, item in enumerate(self.result):
            d = dict()
            for key,value in enumerate(item.values()[0]):
                l = item.values()[0][value]
                d['min_%s'%value] = l[0][0]
                d['max_%s'%value] = l[0][1]
                d['f_%s'%value] = l[1]
                d['price_unit'] = l[2]
            self.result[ix][item.keys()[0]] = d
