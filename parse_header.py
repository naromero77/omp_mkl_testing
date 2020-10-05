#!/usr/bin/env python3

import re,os

def comment_remover(text):
    '''
    https://stackoverflow.com/a/241506
    '''
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def hash_remover(text):
    '''
    https://stackoverflow.com/a/241506
    '''
    def replacer(match):
        s = match.group(0)
        if (s.startswith('/') or s.startswith('#')):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"|#[^\r\n]*(?:\\\r?\n[^\r\n]*)*',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(r'\n\s*\n', '\n', re.sub(pattern, replacer, text),flags=re.MULTILINE)

def matchall(fstr):
    #m=re.finditer(r"(\w+)\s*(\w+)\s*\(([^;]+)\)\s*([^;]*);",fstr,re.MULTILINE)
    #m=re.finditer(r"^(\w+)\s+(\w+)\s*\((.*?)\)",fstr,re.MULTILINE | re.DOTALL)
    #m=re.finditer(r"\b^(?!#)([\s\w]+?)\s+(\w+)\s?\((.*?)\)",fstr,re.MULTILINE | re.DOTALL)
    #m=re.finditer(r"^(.+?)\s(\w+)\s?\((.*?)\)",fstr,re.MULTILINE | re.DOTALL)
    m=re.finditer(r"^([\w\s]+)\s(\w+)\s?\((.*?)\)",fstr,re.MULTILINE | re.DOTALL)
    return m
def hclean(fpath):
    '''
    read and clean up header file
    return list of strings (each string is a function signature)

    assumes any function declaration spanning multiple lines has a comma
      (and possibly whitespace) at the end of each broken line
    '''
    with open(fpath,'r') as f:
        d0=f.read()

    #put signature on one line (assume multiline signature has comma at end of each broken line)
    d0=re.sub(',\s+',',',d0)

    #clean up extra spaces
    #d0=re.sub(' +',' ',d0)

    # split on newline
    # remove blank lines
    # remove lines beginning with #
    d0=list(filter(lambda x:x[0]!="#",filter(None,d0.split('\n'))))

    # only keep lines that end with ';'
    d0=list(filter(lambda x:x[-1]==';',d0))
    return d0

# 
# use r"(\w+)\s*(\w+)\s*\(([^;]+)\)\s*([^;]*);" to match multiline declaration (if hclean doesn't work)
# 

def fparse(m):
    '''
    TODO: fix for types with spaces (e.g. "long int", "unsigned int", etc.)
    parse string containing function signature
    returns:
    [ function_name,
      return_type,
      [[type_var1, is_const_var1, name_var1],
       [type_var2, is_const_var2, name_var2],
        ...
      ]
    ]  
    '''
    rtype = m.group(1)
    fname = m.group(2)
    args = m.group(3).split(',')
    nargs = len(args)
    argvars = []
    for arg in args:
        larg = arg.split()
        isconst = (larg[0] == 'const')
        if isconst:
            larg.pop(0)
        varname = larg.pop()
        vartype = larg.pop()
        npt = varname.count('*')
        varname = varname[npt:]
        vartype = vartype + npt*'*'
        argvars.append([vartype,isconst,varname])
    # depending on what is needed, can append the result to the variable list for non-void
    #if rtype.lower()!="void":
    #    argvars.append([rtype,False,'RESULT'])

    return (fname,rtype,argvars)

if __name__ == '__main__':
    #mklh=os.path.join(os.environ['MKLROOT'],'include','mkl_blas.h')
    #mklh=os.path.join(os.environ['MKLROOT'],'include','mkl_blas_omp_offload.h')
    #mklh=os.path.join(os.environ['MKLROOT'],'include','mkl_cblas.h')
    mklh='../mkl_cblas.h'
    with open(mklh,'r') as f:
        mklstr = f.read()

    m=matchall(hash_remover(mklstr))
    for i,mi in enumerate(m):
        print(f"\n{i}:\n{mi.group(0)}\n")
        n,t,v = fparse(mi)
        print(n)
        print(t)
        # uncomment to transpose args
        #v = list(zip(*v))
        for j in v:
            print(j)
