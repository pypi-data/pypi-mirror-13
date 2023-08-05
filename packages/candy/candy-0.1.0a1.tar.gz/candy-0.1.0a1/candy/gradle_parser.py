import ply.lex as lex
import re

class MyLexer(object):
    """ The lexer for Gradle scripts (Groovy), modified from
    https://github.com/musiKk/plyj/blob/master/plyj/parser.py

    This lexer captures all tokens, including whitespace and newlines.
    Printing all tokens would exactly reproduce the original input text
    """

    keywords = ('this', 'class', 'void', 'super', 'extends', 'implements', 'enum', 'interface',
                'byte', 'short', 'int', 'long', 'char', 'float', 'double', 'boolean', 'null',
                'true', 'false',
                'final', 'public', 'protected', 'private', 'abstract', 'static', 'strictfp', 'transient', 'volatile',
                'synchronized', 'native',
                'throws', 'default',
                'instanceof',
                'if', 'else', 'while', 'for', 'switch', 'case', 'assert', 'do',
                'break', 'continue', 'return', 'throw', 'try', 'catch', 'finally', 'new',
                'package', 'import'
                )

    tokens = [
        'NAME',
        'NUM',
        'STRING_LITERAL',
        'LINE_COMMENT', 'BLOCK_COMMENT',

        'OR', 'AND',
        'EQ', 'NEQ', 'GTEQ', 'LTEQ',
        'LSHIFT', 'RSHIFT', 'RRSHIFT',

        'TIMES_ASSIGN', 'DIVIDE_ASSIGN', 'REMAINDER_ASSIGN',
        'PLUS_ASSIGN', 'MINUS_ASSIGN', 'LSHIFT_ASSIGN', 'RSHIFT_ASSIGN', 'RRSHIFT_ASSIGN',
        'AND_ASSIGN', 'OR_ASSIGN', 'XOR_ASSIGN',

        'PLUSPLUS', 'MINUSMINUS',

        'ELLIPSIS',

        'WHITESPACES'
    ] + [k.upper() for k in keywords]

    literals = '()+-*/=?:,.^|&~!=[]{};<>@%'

    t_NUM = r'\.?[0-9][0-9eE_lLdDa-fA-F.xXpP]*'
    t_STRING_LITERAL = r'[\"\']([^\\\n]|(\\.))*?[\"\']'

    t_LINE_COMMENT = '//.*'
    t_BLOCK_COMMENT = r'/\*(.|\n)*?\*/'

    t_OR = r'\|\|'
    t_AND = '&&'

    t_EQ = '=='
    t_NEQ = '!='
    t_GTEQ = '>='
    t_LTEQ = '<='

    t_LSHIFT = '<<'
    t_RSHIFT = '>>'
    t_RRSHIFT = '>>>'

    t_TIMES_ASSIGN = r'\*='
    t_DIVIDE_ASSIGN = '/='
    t_REMAINDER_ASSIGN = '%='
    t_PLUS_ASSIGN = r'\+='
    t_MINUS_ASSIGN = '-='
    t_LSHIFT_ASSIGN = '<<='
    t_RSHIFT_ASSIGN = '>>='
    t_RRSHIFT_ASSIGN = '>>>='
    t_AND_ASSIGN = '&='
    t_OR_ASSIGN = r'\|='
    t_XOR_ASSIGN = '\^='

    t_PLUSPLUS = r'\+\+'
    t_MINUSMINUS = r'\-\-'

    t_ELLIPSIS = r'\.\.\.'

    t_WHITESPACES = '[ \t\f]+'

    def t_NAME(self, t):
        '[A-Za-z_$][A-Za-z0-9_$]*'
        if t.value in MyLexer.keywords:
            t.type = t.value.upper()
        return t

    t_newline = r'\n+'
    t_newline2 = r'(\r\n)+'

    def t_error(self, t):
        print("Illegal character '{}' ({}) in line {}".format(t.value[0], hex(ord(t.value[0])), t.lexer.lineno))
        t.lexer.skip(1)


class GradleParser:
    """ A gradle script parser that has the capability to manipulate only the dependency section

    """
    def __init__(self):
        self.lexer = lex.lex(module=MyLexer(), optimize=True)
        self.section0 = None
        self.dependency_section = None
        self.section1 = None

    def parse(self, file_path):
        """ Parse a build.gradle script into three sections

        :param file_path: the path to the script
        :return: True if successful
        """
        with open(file_path) as f:
            self.lexer.input(f.read())
        tokens = [t.value for t in self.lexer]
        # extract dependency section, an ugly parser, better with yacc
        level = 0  # the {} nest level
        begin = None  # the beginning position of the dependency section
        for i in range(len(tokens)):
            t = tokens[i]
            if t == '{':
                level += 1
            elif t == '}':
                level -= 1
            if level == 0 and t == "dependencies":
                begin = i
                break
        if begin is None:
            # there is no dependency section, add a new one
            self.section0 = tokens
            self.dependency_section = ["dependencies", " ", "{", "\n", "}"]
            self.section1 = ["\n"]
        else:
            end = None
            # find the end
            for i in range(begin, len(tokens)):
                t = tokens[i]
                if t == '{':
                    level += 1
                elif t == '}':
                    level -= 1
                    if level == 0:
                        end = i
                        break
            if end is None:
                return False
            self.section0 = tokens[:begin]
            self.dependency_section = tokens[begin:end+1]  # to include the ending token
            self.section1 = tokens[end+1:]
        return True

    def add_dependency(self, d):
        """ Add a new dependency to the dependency section

        :param d: the all-in-one dependency text, e.g., com.haha:example:1.0.0+
        """
        if self.find_dependency(d) is not None:
            return
        new_dependency = ['    ', 'compile', ' ', "'%s'" % (d,), '\n']
        l = len(self.dependency_section)
        # the last token is }
        self.dependency_section = self.dependency_section[:l-1] + new_dependency + self.dependency_section[l-1:]

    def remove_dependency(self, d):
        s, lim = self.dependency_section, len(self.dependency_section)
        loc = self.find_dependency(d)
        if loc is None:
            return False
        l, r = None, None
        pattern = re.compile(r'[ \t]+')
        # scan backwards to find last \n
        for i in range(loc, 0, -1):
            t = s[i]
            if t == '\n':
                l = i
                break
        # scan forwards to find first non-whitespace
        for i in range(loc+1, lim):
            t = s[i]
            if pattern.match(t) is None:
                r = i
                break
        if l is None or r is None:
            return False
        self.dependency_section = s[:l] + s[r:]

    def find_dependency(self, d):
        quoted = "'%s'" % (d,)
        s, lim = self.dependency_section, len(self.dependency_section)
        loc = None
        for i in range(lim):
            t = s[i]
            if t == quoted:
                loc = i
        return loc

    def output(self):
        s = ""
        for t in self.section0:
            s += t
        for t in self.dependency_section:
            s += t
        for t in self.section1:
            s += t
        return s

