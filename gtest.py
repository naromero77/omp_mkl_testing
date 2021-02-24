#!/usr/bin/env python3
import jinja2,os,json
import re
from collections import namedtuple

#
#  __                                      _          _
# /__ |  _  |_   _. |     | o ._  o  _.   /   _  ._ _|_ o  _
# \_| | (_) |_) (_| |   \_| | | | | (_|   \_ (_) | | |  | (_|
#                                _|                        _|
#
dirname = os.path.dirname(__file__)
templateLoader = jinja2.FileSystemLoader(searchpath=os.path.join(dirname, "template"))
templateEnv = jinja2.Environment(loader=templateLoader)


template = templateEnv.get_template(f"gemm.cpp.jinja2")
functions = []
# read in the json from the header parser
# Set the directory you want to start from
rootDir = 'data'
for dirName, subdirList, fileList in os.walk(rootDir):
    for fname in fileList:
#        print('\t%s' % fname)
        with open(rootDir+"/"+fname) as f:
            functions.append(json.load(f))
        
# Supported functions
# '.' is equivalent to '?' wildcard
# blas_match = 'cblas_.gemm'
blas_match = 'cblas_.....'
rot_match = 'cblas_.rot.'

for function in functions:
    function_name = function[0]

    # This bit of code will be removed in the future, but for now its just for testing certain functions
    found_blas = re.search(r'\b' + blas_match + r'\b',function_name)
    found_rot = re.search(r'\b' + rot_match + r'\b',function_name)
    if found_blas:
        if found_rot: # don't generate these
            continue
        pass
    else:
        continue

    argument_types = function[1]
    argument_intents = function[2]
    argument_names = function[3]
    argument_sizes = function[4]
    print(f'{function_name}, {argument_types}, {argument_intents} {argument_sizes}')
    print('argument_sizes = ', argument_sizes)

    # sanity check
    if len(argument_types) != len(argument_intents) or len(argument_types) != len(argument_names) or len(argument_intents) != len(argument_names):
        print("length problem!")
        exit()

    l_aggregate_input_ = []
    l_scalar_input_ = []
    l_input_output_ = []
    l_return_ = []
    l_output_ = []
    l_types_names_ = []
    # look at argument types and intents
    for atype, intent, name, size  in zip(argument_types,argument_intents,argument_names,argument_sizes) :
        if intent != "return":
            if "*" in atype:
                l_types_names_.append( [size,True, intent,atype[:len(atype)-1], name] )
            else:
                l_types_names_.append( [size,False, intent,atype, name] )

        if intent == "in":
            if "*" in atype:
                l_aggregate_input_.append([size,atype[:len(atype)-1], name ])
            else:
                # check if size is a single char and add single quotes
                # for handling the FortranAPI
                try:
                    size.isalpha()
                    if len(size) == 1:
                        size = '\'' + size + '\''
                except AttributeError:
                    pass
                l_scalar_input_.append([size,atype, name ])
            
        elif intent == "inout" or intent == "out":
# inout is probably always a pointer, at least in C
            l_input_output_.append([size,atype[:len(atype)-1], name ])
        elif intent == "out":
            l_output_.append([size,atype[:len(atype)-1], name ])
        elif intent == "return":
# sanity check on length of l_return_. it should only ever have one
# output.
            if len(l_return_) > 1:
                print("problem, too many outputs")
                exit()
            l_return_.append([size,atype, name ])
        else:
            print("problem!")
            exit()

    l_unique_type_ = set(t_ for size_,pointer_,intent_,t_,name_ in l_types_names_ if intent_ == "out" or intent_ == "inout")
    
    for size_,t_,name_ in l_return_:
        l_unique_type_.add(t_)

  #  debug all the inputs
    print(f'function_name: {function_name}')
    print(f'l_aggregate_input_ {l_aggregate_input_}')
    print(f'l_scalar_input_ {l_scalar_input_}')
    print(f'l_input_output_ {l_input_output_}')
    print(f'l_return_ {l_return_}')
    print(f'l_output_ {l_output_}')
    print(f'l_type_names_ {l_types_names_}')
    print(f'l_unique_type_ {l_unique_type_}')

    str_ = template.render( name_function=function_name,
                            l_aggregate_input=l_aggregate_input_,
                            l_scalar_input=l_scalar_input_,
                            l_input_output=l_input_output_,
                            l_return=l_return_,
                            l_output=l_output_,
                            l_types_names=l_types_names_,
                            l_unique_type=l_unique_type_ )
    with open(f"{function_name}.cpp", 'w') as f:
        f.write(str_)


