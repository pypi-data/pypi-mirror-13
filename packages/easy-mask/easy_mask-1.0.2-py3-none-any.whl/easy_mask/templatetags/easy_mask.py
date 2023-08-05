from django import template

register = template.Library()


class RegexPhone():
    @register.filter(name='phone')
    def phone(Regex):
        """ Return (00) 0000-0000 or (00) 00000-0000 """
        try:
            if len(Regex) >=11:
                a = Regex[0:2]
                b = Regex[2:7]
                c = Regex[7:11]
                return '(' + a + ')' + ' ' + b + '-' + c
            else:
                a = Regex[0:2]
                b = Regex[2:6]
                c = Regex[6:10]
                return '(' + a + ')' + ' ' + b + '-' + c
        except ValueError:
            print('error in the counting of numeric characters')


class RegexCPF():
    @register.filter(name='cpf')
    def cpf(Regex):
        """ Return 000.000.000-00 """
        a = Regex[0:3]
        b = Regex[3:6]
        c = Regex[6:9]
        d = Regex[9:11]
        return a + '.' + b + '.' + c + '-' + d


class RegexRG():
    @register.filter(name='rg')
    def rg(Regex):
        """ Return 00.000.000-0 or 0.000.000 or 0.000.000-00 """
        pass


class RegexCNPJ():
    @register.filter(name='cnpj')
    def cnpj(Regex):
        """ Return 00.000.000/0000-00 """
        a = Regex[0:2]
        b = Regex[2:5]
        c = Regex[5:8]
        d = Regex[8:12]
        e = Regex[12:14]
        return a + '.' + b + '.' + c + '/' + d + '-' + e


class RegexCEP():
    @register.filter(name='cep')
    def cep(Regex):
        """ Return 00000-000 """
        a = Regex[0:5]
        b = Regex[5:8]
        return a + '-' + b
