import ply.lex as lex
import ply.yacc as yacc

# --- Análisis Léxico ---

tokens = (
    'INT', 'FLOAT', 'CHAR', 'STRING', 'NAME', 'NUMBER', 'FLOAT_NUMBER',
    'CHAR_VALUE', 'STRING_VALUE',
    'EQUALS', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'SEMICOLON'
)

t_ignore = ' \t'

t_EQUALS = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_SEMICOLON = r';'

def t_INT(t):
    r'\bint\b'
    return t

def t_FLOAT(t):
    r'\bfloat\b'
    return t

def t_CHAR(t):
    r'\bchar\b'
    return t

def t_STRING(t):
    r'\bstring\b'
    return t

def t_FLOAT_NUMBER(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_CHAR_VALUE(t):
    r"'.'"
    t.value = t.value[1]
    return t

def t_STRING_VALUE(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

# --- Análisis Sintáctico ---

# Definición de una clase para los nodos del árbol
class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.leaf = leaf

# Tabla de símbolos
symbol_table = {}

def add_to_symbol_table(name, var_type, value=None):
    if name in symbol_table:
        raise ValueError(f"Variable '{name}' ya declarada")
    symbol_table[name] = {"type": var_type, "value": value}

def check_and_convert_type(value, var_type):
    if var_type == "int":
        if isinstance(value, int):
            return value
        else:
            raise TypeError("No se puede asignar un valor no entero a una variable de tipo int")
    elif var_type == "float":
        if isinstance(value, (int, float)):
            return float(value)
        else:
            raise TypeError("Tipo incompatible para float")
    elif var_type == "char":
        if isinstance(value, str) and len(value) == 1:
            return value
        else:
            raise TypeError("Tipo incompatible para char")
    elif var_type == "string":
        if isinstance(value, str):
            return value
        else:
            raise TypeError("Tipo incompatible para string")
    else:
        raise ValueError("Tipo desconocido")

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE')
)

# Gramática y construcción del árbol

def p_program(p):
    '''program : statement_list'''
    p[0] = Node('program', [p[1]])

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 3:
        p[1].children.append(p[2])
        p[0] = p[1]
    else:
        p[0] = Node('statement_list', [p[1]])

def p_statement(p):
    '''statement : decl
                 | assign'''
    p[0] = Node('statement', [p[1]])

def p_decl(p):
    '''decl : type NAME SEMICOLON'''
    add_to_symbol_table(p[2], p[1])
    p[0] = Node('decl', [Node('type', [], p[1]), Node('name', [], p[2])])

def p_assign(p):
    '''assign : NAME EQUALS expression SEMICOLON'''
    if p[1] not in symbol_table:
        raise ValueError(f"Variable '{p[1]}' no declarada")
    
    var_type = symbol_table[p[1]]["type"]
    converted_value = check_and_convert_type(p[3].leaf, var_type)
    symbol_table[p[1]]["value"] = converted_value
    p[0] = Node('assign', [Node('name', [], p[1]), Node('expression', [p[3]])])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    if p[2] == '+':
        p[0] = Node('expression', [p[1], Node('op', [], p[2]), p[3]], leaf=p[1].leaf + p[3].leaf)
    elif p[2] == '-':
        p[0] = Node('expression', [p[1], Node('op', [], p[2]), p[3]], leaf=p[1].leaf - p[3].leaf)
    elif p[2] == '*':
        p[0] = Node('expression', [p[1], Node('op', [], p[2]), p[3]], leaf=p[1].leaf * p[3].leaf)
    elif p[2] == '/':
        p[0] = Node('expression', [p[1], Node('op', [], p[2]), p[3]], leaf=p[1].leaf / p[3].leaf)

def p_expression_number(p):
    '''expression : NUMBER
                  | FLOAT_NUMBER
                  | CHAR_VALUE
                  | STRING_VALUE'''
    p[0] = Node('number', [], leaf=p[1])

def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR
            | STRING'''
    p[0] = p[1]

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}' on line {p.lineno}")
    else:
        print("Error sintactico - posiblemente falta un ';' en la linea "+f'{lexer.lineno-2}')

parser = yacc.yacc()

# Función para imprimir el árbol
def print_tree(node, level=0):
    if node is not None:
        print('  ' * level + node.type, end='')
        if node.leaf is not None:
            print(' (' + str(node.leaf) + ')')
        else:
            print()
        for child in node.children:
            print_tree(child, level + 1)

# --- Ejecución y Pruebas ---

code = '''
int x;
float y;
char z;
string w;
x = 4;
y = 5.2 + 3;
z = 'a';
w = "hola";
'''

try:
    # Analizar el código y construir el árbol
    root = parser.parse(code, lexer=lexer)

    # Mostrar el árbol sintáctico
    print("\nÁrbol Sintáctico:")
    print_tree(root)

    # Mostrar la tabla de símbolos
    print("\n( valores finales):")
    for var, info in symbol_table.items():
        print(f"{var} (tipo: {info['type']}): valor = {info['value']}")

except ValueError as e:
    print(f"Error: {e}")
except TypeError as e:
    print(f"Error: {e}")
