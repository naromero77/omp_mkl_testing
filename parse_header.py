#!/usr/bin/env python3

import re,os


def hclean(fpath):
    '''
    read and clean up header file
    return list of strings (each string is a function signature)
    '''
    with open(fpath,'r') as f:
        d0=f.read()
    #put signature on one line (assume multiline signature has comma at end of each broken line)
    d0=re.sub(',\s+',',',d0)
    #clean up extra spaces
    #d0=re.sub(' +',' ',d0)
    # remove blank lines and #
    d0=list(filter(lambda x:x[0]!="#",filter(None,d0.split('\n'))))
    # only keep lines that end with ';'
    d0=list(filter(lambda x:x[-1]==';',d0))
    return d0


# use r"(\w+)\s*(\w+)\s*\(([^;]+)\)\s*([^;]*);" to parse without cleaning whitespace
def fparse(s):
    '''
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
    m=re.search(r"(\w+)\s(\w+)\s?\((.+)\)",s)
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
    mklh=os.path.join(os.environ['MKLROOT'],'include','mkl_blas.h')
    #mklh='mkl_blas.h'
    d=hclean(mklh)
    #types = set(i.split()[0] for i in d)
    for i,l in enumerate(d):
        print(i)
        print(l)
        n,t,v = fparse(l)
        #v = list(zip(*v))
        print(n)
        print(t)
        print(v)
