#!/usr/bin/env python3
import jinja2,os
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


template = templateEnv.get_template(f"sdot2.cpp.jinja2")

blas1 = [
    ["ddot",
     [ "int", "double*", "int", "double*", "int","double"],
     [ "in", "in", "in", "in", "in", "return" ],
     [ "n", "dx", "incx", "dy", "incy", "result"],
     [ "1", "n", "1", "n", "1", "1"] ],
    ["dnrm2",
     [ "int", "double*", "int", "double"],
     [ "in", "in", "in", "return" ],
     [ "n", "x", "incx", "result"],
     [ "1", "n", "1", "1", "1"] ],
    ["drotg",
     [ "double*", "double*", "double*", "double*"],
     [ "inout", "inout", "out", "out" ],
     [ "da", "db", "c", "s"],
     [ "1","1", "1", "1"] ],
    ["sdot",
     [ "int", "float*", "int", "float*", "int","float"],
     [ "in", "in", "in", "in", "in", "return" ],
     [ "n", "dx", "incx", "dy", "incy", "result"],
     [ "1", "n", "1", "n", "1", "1"] ]
 ]

for function in blas1:
    function_name = function[0]
    argument_types = function[1]
    argument_intents = function[2]
    argument_names = function[3]
    argument_sizes = function[4]
    print(f'{function_name}, {argument_types}, {argument_intents} {argument_sizes}')

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

    


# for name_,input_t_,both_input_output_variables,return_scalar_variable in [["ddot", "double", False,True], ["sdot", "float",False,True] ]:
# # variables that are pure inputs
#     l_input_=[[input_t_,"x"],[input_t_,"y"]]
# # variables that are both inputs and outputs
#     if both_input_output_variables:
#         l_input_inout_=[[input_t_,"z"]]
#     else:
#         l_input_inout_=[]
# # variables that are pure outputs
#     if return_scalar_variable:
#         return_output_=[input_t_,"result"]
#     else:
#         return_output_= None

#     l_aggregate_output_=[[input_t_,"x"],[input_t_,"y"]]
# #    l_aggregate_output_=[]

#     if return_output_:
#         l_unique_output_type_ = set(t_ for t_,name_ in l_aggregate_output_+[return_output_])
#     else:
#         l_unique_output_type_ = set(t_ for t_,name_ in l_aggregate_output_)

#     str_ = template.render( name_function=name_,
#                             t=input_t_,
#                             l_input=l_input_,
#                             l_input_inout=l_input_inout_,
#                             return_output=return_output_,
#                             l_aggregate_output=l_aggregate_output_,
#                             l_unique_output_type=l_unique_output_type_ )
#     with open(f"{name_}_{input_t_}.cpp", 'w') as f:
#         f.write(str_)
