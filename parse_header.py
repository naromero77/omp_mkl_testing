#!/usr/bin/env python3

import re,os

def clean(text):
    '''
    remove comment, #, and blank lines
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

def get_decls(fstr):
    '''
    match all function declarations
    '''
    m=re.finditer(r"^([\w\s]+)\s(\w+)\s?\((.*?)\)",fstr,re.MULTILINE | re.DOTALL)
    return m

def hclean(fpath):
    '''
    read and clean up header file
    '''
    with open(fpath,'r') as f:
        t=f.read()
    return clean(t)


def fparse(m):
    '''
    TODO: fix for types with spaces (e.g. "long int", "unsigned int", etc.)
    TODO: value->in, const->in, ref(no const)->inout, result->return
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
    if rtype.lower()!="void":
        argvars.append([rtype,False,'RESULT'])

    return (fname,rtype,argvars)

if __name__ == '__main__':
    #mklh=os.path.join(os.environ['MKLROOT'],'include','mkl_blas.h')
    #mklh=os.path.join(os.environ['MKLROOT'],'include','mkl_blas_omp_offload.h')
    #mklh=os.path.join(os.environ['MKLROOT'],'include','mkl_cblas.h')
    mklh='../mkl_cblas.h'
    mklstr = hclean(mklh)

    m=get_decls(mklstr)

    for i,mi in enumerate(m):
        print(f"\n{i}:\n{mi.group(0)}\n")
        n,t,v = fparse(mi)
        print(n)
        print(t)
        # uncomment to transpose args
        #v = list(zip(*v))
        for j in v:
            print(j)
