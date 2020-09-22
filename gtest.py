#!/usr/bin/env python3
import jinja2,os

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
     [ "in", "in", "in", "in", "in", "out" ],
     [ "n", "dx", "incx", "dy", "incy", "result"] ]
 ]

for function in blas1:
    function_name = function[0]
    argument_types = function[1]
    argument_intents = function[2]
    argument_names = function[3]
    print(f'{function_name}, {argument_types}, {argument_intents}')

    # sanity check
    if len(argument_types) != len(argument_intents) or len(argument_types) != len(argument_names) or len(argument_intents) != len(argument_names):
        print("length problem!")
        exit()

    l_aggregate_input_ = []
    l_scalar_input_ = []
    l_input_output_ = []
    l_output_ = []
    # look at argument types and intents
    for atype, intent, name  in zip(argument_types,argument_intents,argument_names) :
        if intent == "in":
            if "*" in atype:
                l_aggregate_input_.append([atype[:len(atype)-1], name ])
            else:
                l_scalar_input_.append([atype, name ])
        elif intent == "inout":
            l_input_output_.append([atype, name ])
        elif intent == "out":
# sanity check on length of l_output_. it should only ever have one
# output.
            if len(l_output_) > 1:
                print("problem, too many outputs")
                exit()
            l_output_.append([atype, name ])
        else:
            print("problem!")
            exit()
            
    str_ = template.render( name_function=function_name,
                            l_aggregate_input=l_aggregate_input_,
                            l_scalar_input=l_scalar_input_,
                            l_input_output=l_input_output_,
                            l_output=l_output_[0] )
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
