import re
from pygments.lexer import RegexLexer
from pygments.token import Text, Comment, Operator, Keyword, Name, String, Number, Token

__all__ = ["CypherLexer"]

class CypherLexer(RegexLexer):
    name = 'Cypher'
    aliases = ['cypher']
    filenames = ['*.cyp', '*.cypher']

    flags = re.IGNORECASE
    tokens = {
        'root': [
            (r'\s+', Text),
            (r'//.*?\n', Comment.Single),
            (r'\b(ABS|ACOS|ALL|ALLSHORTESTPATHS|AND|ANY|AS|ASC|ASCENDING|ASIN|ASSERT|ATAN|ATAN2|AVG'
             r'|BY'
             r'|CASE|CEIL|COALESCE|COLLECT|COMMIT|CONSTRAINT|CONTAINS|COS|COT|COUNT|CREATE|CYPHER'
             r'|DEGREES|DELETE|DESC|DESCENDING|DETACH|DISTINCT|DROP'
             r'|E|ELSE|END|ENDNODE|ENDS|EXISTS|EXP|EXPLAIN|EXTRACT'
             r'|FALSE|FIELDTERMINATOR|FILTER|FLOOR|FOREACH|FROM'
             r'|HAS|HAVERSIN|HEAD|HEADERS'
             r'|ID|ILIKE|IN|INDEX|IS'
             r'|KEYS'
             r'|LABELS|LAST|LEFT|LENGTH|LIKE|LIMIT|LOAD CSV|LOG|LOG10|LOWER|LTRIM'
             r'|MATCH|MAX|MERGE|MIN'
             r'|NODE|NODES|NONE|NOT|NULL'
             r'|ON|OPTIONAL|OR|ORDER'
             r'|PERCENTILECONT|PERCENTILEDISC|PERIODIC|PI|PROFILE'
             r'|RADIANS|RAND|RANGE|REDUCE|REL|RELATIONSHIP|RELATIONSHIPS|REMOVE|REPLACE|RETURN|RIGHT|ROUND|RTRIM'
             r'|SCAN|SET|SHORTESTPATH|SIGN|SIN|SINGLE|SIZE|SKIP|SPLIT|SQRT|START|STARTNODE|STARTS|STDEV|STDEVP|STR|SUBSTRING|SUM'
             r'|TAIL|TAN|THEN|TIMESTAMP|TOFLOAT|TOINT|TRIM|TRUE|TYPE'
             r'|UNION|UNIQUE|UNWIND|USING|UPPER'
             r'|WHEN|WHERE|WITH'
             r'|XOR)\b', Keyword),
            (r'[+*/<>=~!@#%^&|`?-]', Operator),
            (r'[0-9]+', Name),
            (r"'(''|[^'])*'", String.Single),
            (r'"(""|[^"])*"', String.Symbol),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', Name),
            (r'[-\)\]]-[>\(]|[<\)]-[-\(\[]|[\]\)]-|-[\(\[]|-->|<--|\]-|-\[|\)<-\[', Token.Pattern),
            (r'\.', Token.Pattern),
            (r'\(|\)|\]|\[|{|}', Token.Pattern)
        ]
    }