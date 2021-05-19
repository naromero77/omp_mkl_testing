#!/usr/bin/env python3

import re,os
import math

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

def varvalues(varname, vartype):
    '''
    Generate function sizes from function header info. This covers the cblas interfaces only at this time.

    Pointers types are gives sizes, but scalars are given initial values.

    Inputs is the variable name from the header file as obtain by fparse function.

    Input parameters are not checked for compatbility with the MKL function that used them.
    Some incompatibilities are noted and enforced with assert statements.
    '''

    FortranAPI = False # controls some operations, e.g. transpose, uplo,
    # some scalar values that can be reused, we intentionaly pick 45 degrees because
    # sin(45) = cos(45)
    rotAngle = math.radians(45)
    realScalar = rotAngle
    imagScalar = rotAngle*1j
    # default input sizes
    # gemm, gemv, axpy, etc.
    dimM = 1000
    dimN = 1000
    dimK = 1000  # needs to be set manually to half-width due to ?TB?V functions
    dimX = 1000
    dimY = 1000
    # dimensions are currently constrained because matrix dimensions are not
    # consistently name, e.g. dimA = M-by-K in some routines and M-by-N in others
    assert (dimM == dimN == dimK == dimX == dimY)
    incX = 1
    incY = 1
    alphaReal = realScalar
    betaReal = realScalar
    LDA = max(1,dimM) # Trans = N; otherwise max(1,dimK)
    # LDB = max(1,dimK) # Trans = N; oterhwise max(1,dimN)
    LDB = max(1,dimN) # Trans = T; choose this one to satisy all constraints
    LDC = max(1,dimM)
    matA = dimM*dimK
    matB = dimK*dimM
    matC = dimM*dimN
    matAp = dimN*dimN
    vecX = dimX
    vecY = dimY
    KL = 1 # sub-diagonal, unsure of reasonable values
    KU = 1 # super-diagonal. unsure of reasonable values
    # rotations
    rotCos = math.cos(rotAngle)
    rotSin = math.sin(rotAngle)
    # strings that control operations
    # FortranAPI
    if FortranAPI:
        Trans = 'N'
        TransA = 'N'
        TransB = 'T'
        Uplo = 'U'
        Side = 'L'
        Diag = 'U' # need to be fixed
    else: # CblasAPI
        Trans = 'CblasNoTrans'
        TransA = 'CblasNoTrans'
        TransB = 'CblasTrans'
        Uplo = 'CblasUpper'
        Side = 'CblasLeft'
        Diag = 'CblasNonUnit'
        Layout = 'CblasColMajor' # only exists for Cblas API, make it behave like the Fortran API
    result = 1

    # Coverage for batch and batch_strided interfaces are needed here
    '''
    ["cblas_zgemm_batch", ["CBLAS_LAYOUT", "CBLAS_TRANSPOSE*", "CBLAS_TRANSPOSE*", "MKL_INT*", "MKL_INT*", "MKL_INT*", "void*", "void**", "MKL_INT*", "void**", "MKL_INT*", "void*", "void**", "MKL_INT*", "MKL_INT", "MKL_INT*"], ["in", "in", "in", "in", "in", "in", "in", "in", "in", "in", "in", "in", "inout", "in", "in", "in"], ["Layout", "TransA_Array", "TransB_Array", "M_Array", "N_Array", "K_Array", "alpha_Array", "A_Array", "lda_Array", "B_Array", "ldb_Array", "beta_Array", "C_Array", "ldc_Array", "group_count", "group_size"]]

    ["cblas_zgemm_batch_strided", ["CBLAS_LAYOUT", "CBLAS_TRANSPOSE", "CBLAS_TRANSPOSE", "MKL_INT", "MKL_INT", "MKL_INT", "void*", "void*", "MKL_INT", "MKL_INT", "void*", "MKL_INT", "MKL_INT", "void*", "void*", "MKL_INT", "MKL_INT", "MKL_INT"], ["in", "in", "in", "in", "in", "in", "in", "in", "in", "in", "in", "in", "in", "in", "inout", "in", "in", "in"], ["Layout", "TransA", "TransB", "M", "N", "K", "alpha", "A", "lda", "stridea", "B", "ldb", "strideb", "beta", "C", "ldc", "stridec", "batch_size"]]
    '''

    # conveter inputs to lower case in order to look them up in dictionary
    # Note that the same variable name can mean two different things, e.g.
    # 'C' is used as a matrix, and 'c' is used a scalar in the MKL header files

    varnameLower = varname.lower()

    name2value = {
        'm' : dimM,
        'n' : dimN,
        'k' : dimK,
        'incx' : incX,
        'incy' : incY,
        'alpha': alphaReal,
        'beta' : betaReal,
        'lda' : LDA,
        'ldb' : LDB,
        'ldc' : LDC,
        'a' : matA,
        'b' : matB,
        'c' : matC,
        'ap': matAp,
        'x' : vecX,
        'dx' : vecX,
        'y' : vecY,
        'dy' : vecY,
        'kl' : KL,
        'ku' : KU,
        'trans' : Trans,
        'transa' : TransA,
        'transb' : TransB,
        'uplo' : Uplo,
        'side' : Side,
        'diag' : Diag,
        'layout' : Layout,
        's' : rotSin,
    }

    # variable names that can map to more than one data type
    # the following assumptions are made above:
    # - assume c is a matrix above, but could also be rotCos
    # - s, alpha and beta, can be real or complex-valued
    degeneratenames = ['c', 's', 'alpha', 'beta']

    supportedTypes = ['char*',
                      'MKL_INT',
                      'MKL_INT*',
                      'MKL_Complex8*',
                      'MKL_Complex16*',
                      'float',
                      'float*',
                      'double',
                      'double*',
                      'double**',
                      'void*',
                      'CBLAS_LAYOUT',
                      'CBLAS_SIDE',
                      'CBLAS_UPLO',
                      'CBLAS_TRANSPOSE',
                      'CBLAS_DIAG',
    ]

    # create some shorthand groups
    realScalarTypes = ['double', 'float']
    complexScalarTypes = ['MKL_Complex8*', 'MKL_Complex16*']
    pointerTypes = ['double*', 'float*']
    pointerPointerTypes = ['double**', 'float**']

    # rstrip() is needed below to strip white spaces
    tmp_vartype = vartype.rstrip()
    try:
        assert tmp_vartype in supportedTypes
    except AssertionError:
        print(tmp_vartype, " is an unknown datatype")

    try:
        varvalue = name2value[varnameLower]
    except KeyError:
        print(varname, " cannot be initialized")
        varvalue = 'None'

    # super confusing piece of code.
    # Same variable name is used for scalar and pointers (degeneratenames).
    # Additionally, header files set both complex scalars and complex pointers
    # to complex pointers, i.e. MKL_Complex8* and MKL_Complex16*
    # Lastly, json files CANNOT handle complex values
    if varnameLower in degeneratenames:
        if tmp_vartype in realScalarTypes:
            varvalue = realScalar
        elif tmp_vartype in complexScalarTypes: #json unable to handle complex values, initialize complex scalars to real
            if varnameLower != "c": # another special case to deal with because of the way complex scalars are pointers are both set to complex pointers
                varvalue = realScalar
        elif tmp_vartype in pointerTypes:
            pass
            # print("Vartype is double-precision/single-precision pointer")
        elif tmp_vartype in pointerPointerTypes:
            pass
            # print("Vartype is double-precision pointer of pointers")
        else:
            print(varname, "is on degenerate names list but datatype unknown:", tmp_vartype)

    return varvalue


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
        # number of pointers
        npt = varname.count('*')
        varname = varname[npt:]
        # deal with complex scalars and pointers in two stages:
        # - convert void to complex data type
        # - distinguish scalars and pointers after determing varvalue
        #
        # first stage
        # headers use void for both single and double-precision complex
        # make distinction here based on the function name, we check
        # the first character and the seventh character and convert
        # to MKL_Complex8 or MKL_Complex16
        if vartype == "void":
            if (fname[0] == "c" or fname[6] == "c"):
                vartype="MKL_Complex8"
            if (fname[0] == "z" or fname[6] == "z"):
                vartype="MKL_Complex16"
        vartype = vartype + npt*'*'
        varinout = "in" if (isconst or (npt==0)) else "inout"
        varvalue = varvalues(varname, vartype)
        # second stage
        # header files use void* for complex scalar and complex pointers
        # make distinction after determining varvalue and adjust vartype
        # accordingly. If varvalue is float, that complex type will be scalar
        # otherwise, it is the initialization value for a scalar
        if isinstance(varvalue, float):
            # MKL_Complex8*  -> MKL_Complex8
            # MKL_Complex16* -> MKL_Complex16
            vartype = vartype.rstrip("*")
        argvars.append([vartype,varinout,varname,varvalue])
    # depending on what is needed, can append the result to the variable list for non-void
    if rtype.lower()!="void":
        argvars.append([rtype,"return","result","None"])

    return (fname,rtype,argvars)

if __name__ == '__main__':
    import json
    try:
        MKLROOT = os.environ['MKLROOT']
    except KeyError:
        print("MKLROOT variable not set. Trying loading the oneAPI SDL")
        raise

    #mklh=os.path.join(MKLROOT,'include','mkl_blas.h')
    mklh=os.path.join(MKLROOT,'include','mkl_blas_omp_offload.h')
    #mklh=os.path.join(MKLROOT,'include','mkl_cblas.h')
    #mklh='../mkl_cblas.h'
    mklstr = hclean(mklh)

    m=get_decls(mklstr)
    
    jsondir = "data"
    try:
        os.mkdir(jsondir)
    except OSError as error:
        pass

    for i,mi in enumerate(m):
        n,t,v = fparse(mi)
        v = list(zip(*v))
        #print(f"\n{i}:\n{mi.group(0)}\n")
        #print(n)
        #print(t)
        #for j in v:
        #    print(j)
        #print([n,[list(i) for i in v]])
        with open(os.path.join(jsondir,n),'w') as f:
            json.dump([n]+[list(i) for i in v],f)


