########################################################################################################################
#
# PAYLOAD
#
# API functions: payload
#
########################################################################################################################

from __future__ import absolute_import, division, print_function   # , unicode_literals
from six import iteritems
from shutil import copytree
from datetime import datetime


def dostuff(params_values, filepath):
    result = '\n'.join([key + ': ' + str(value) for key, value in iteritems(params_values)])
    with open(filepath, 'w') as filehandle:
        filehandle.write(result)
    return result


###################
# MAIN API FUNCTION
###################

def payload(params_values, output_dir, scratch_dir):

    # print("params_values :", params_values)

    # do stuff with data, saving files into SCRATCH
    ################################################
    result = dostuff(params_values, scratch_dir + 'result.txt')

    # coypy scratch to output_dir, so it is saved as results by basespace
    #####################################################################
    # copytree(source, destination, ignore=_logpath)
    copytree(scratch_dir, output_dir + '../sessiondetails_' + datetime.now().isoformat('_'))
    return result
