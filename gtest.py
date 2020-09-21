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


template = templateEnv.get_template(f"sdot.cpp.jinja2")


for name_,input_t_,both_input_output_variables,return_scalar_variable in [["ddot", "double",False,True], ["sdot", "float",False,True] ]:
# variables that are pure inputs
    l_input_=[[input_t_,"x"],[input_t_,"y"]]
# variables that are both inputs and outputs
    if both_input_output_variables:
        l_input_inout_=[[input_t_,"z"]]
    else:
        l_input_inout_=[]
# variables that are pure outputs
    if return_scalar_variable:
        return_output_=[input_t_,"result"]
    else:
        return_output_= None

    l_aggregate_output_=[[input_t_,"x"],[input_t_,"y"]]
#    l_aggregate_output_=[]

    if return_output_:
        l_unique_output_type_ = set(t_ for t_,name_ in l_aggregate_output_+[return_output_])
    else:
        l_unique_output_type_ = set(t_ for t_,name_ in l_aggregate_output_)

    str_ = template.render( name_function=name_,
                            t=input_t_,
                            l_input=l_input_,
                            l_input_inout=l_input_inout_,
                            return_output=return_output_,
                            l_aggregate_output=l_aggregate_output_,
                            l_unique_output_type=l_unique_output_type_ )
    with open(f"{name_}_{input_t_}.cpp", 'w') as f:
        f.write(str_)
