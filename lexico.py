import tkinter as tk
from tkinter import scrolledtext
from ply import lex, yacc

# Configuración de Tkinter
root = tk.Tk()
root.title("Analizador C++")
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=30, bg='black', fg='white')
text_area.pack()

def mostrar_resultados(resultados):
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.INSERT, resultados)

# Palabras reservadas
reserved = {
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'string': 'STRING',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'return': 'RETURN',
    'for': 'FOR',
    'cout': 'COUT',
}

# Definición de tokens
tokens = [
    'ID', 'NUMERO', 'PUNTO_Y_COMA', 'COMA', 'ASIGNACION', 
    'SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION', 
    'MENOR', 'MAYOR', 'PARENTESIS_IZQ', 'PARENTESIS_DER', 
    'LLAVE_IZQ', 'LLAVE_DER', 'COMENTARIO_LINEA', 'COMENTARIO_BLOQUE',
    'CADENA','INCLUDE', 'AND'
] + list(reserved.values())

# Reglas para tokens simples
t_INCLUDE = r'\#include\s*<[^>]+>'
t_PUNTO_Y_COMA = r';'
t_COMA = r','
t_ASIGNACION = r'='
t_SUMA = r'\+'
t_RESTA = r'-'
t_MULTIPLICACION = r'\*'
t_DIVISION = r'/'
t_MENOR = r'<'
t_MAYOR = r'>'
t_AND=r'&&'
t_PARENTESIS_IZQ = r'\('
t_PARENTESIS_DER = r'\)'
t_LLAVE_IZQ = r'\{'
t_LLAVE_DER = r'\}'
#t_COMENTARIO_LINEA = r'\/\/.*'
#t_COMENTARIO_BLOQUE = r'\/\*[\s\S]*?\*\/'
t_CADENA = r'\"([^\\\n]|(\\.))*?\"'
t_ignore = ' \t\n'

def t_COMENTARIO_BLOQUE(t):
    r'\/\*[\s\S]*?\*\/'
    pass
def t_COMENTARIO_LINEA(t):
    r'\/\/.*'
    pass

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMERO(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t



def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# Reglas del parser
def p_program(p):
    '''program : declaration_list'''
    p[0] = p[1]

def p_declaration_list(p):
    '''declaration_list : declaration_list declaration
                        | declaration'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_declaration(p):
    '''declaration : variable_declaration
                   | function_declaration
                   | statement'''
    p[0] = p[1]

def p_variable_declaration(p):
    '''variable_declaration : type ID PUNTO_Y_COMA
                            | type ID ASIGNACION expression PUNTO_Y_COMA'''
    p[0] = ('var_decl', p[1], p[2], p[4] if len(p) > 4 else None)

def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR
            | STRING'''
    p[0] = p[1]

def p_function_declaration(p):
    'function_declaration : type ID PARENTESIS_IZQ PARENTESIS_DER compound_statement'
    p[0] = ('func_decl', p[1], p[2], p[5])

def p_compound_statement(p):
    '''compound_statement : LLAVE_IZQ statement_list LLAVE_DER'''
    p[0] = ('compound', p[2])

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''statement : expression_statement
                 | compound_statement'''
    p[0] = p[1]

def p_expression_statement(p):
    '''expression_statement : expression PUNTO_Y_COMA'''
    p[0] = ('expr_stmt', p[1])

def p_expression(p):
    '''expression : NUMERO
                  | ID
                  | expression SUMA expression
                  | expression RESTA expression
                  | expression MULTIPLICACION expression
                  | expression DIVISION expression
                  | expression MENOR expression
                  | expression MAYOR expression
                  | ID ASIGNACION expression
                  | COUT MENOR MENOR expression'''
    if len(p) == 2:
        p[0] = ('num' if isinstance(p[1], int) else 'id', p[1])
    elif p[1] == 'cout':
        p[0] = ('cout', p[4])
    else:
        p[0] = ('binop', p[1], p[2], p[3])

def p_error(p):
    print(f"Syntax error at {p.value}")

parser = yacc.yacc()

def analizador(entrada):
    lexer.input(entrada)
    resultados = ""
    while True:
        tok = lexer.token()
        if not tok:
            break
        resultados += f"{tok.type} : {tok.value}\n"
    mostrar_resultados(resultados)

def leer(codigo_fuente):
    with open(codigo_fuente, 'r') as file:
        entrada = file.read()
    analizador(entrada)

codigo = 'prueba.cpp'  # nombre de archivo
leer(codigo)
root.mainloop()
