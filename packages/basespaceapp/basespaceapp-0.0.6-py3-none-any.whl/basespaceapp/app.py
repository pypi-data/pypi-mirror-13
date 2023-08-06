#!/bin/env python

########################################################################################################################
#
# APP
#
# API functions: main
#
# this is a refactored and extended version of the sampleapp.py (the basespace documentation example)
# intended to be run as a script (if __name__ == '__main__': code)
#
########################################################################################################################

from __future__ import absolute_import, division, print_function        # , unicode_literals
import json
import argparse
import os
from six import iteritems
from shutil import copytree
from datetime import datetime
from .config import ARGUMENTS_WITH_CONTENT, ARGUMENTS_WITH_ITEMS


def read_appsession(appsession_jsonfilename):
    """

    :param appsession_jsonfilename:
    :return:
    """
    with open(appsession_jsonfilename) as hdl:
        appsession = json.load(hdl)
    appsessionparams = appsession['Properties']['Items']
    appsessionhref = appsession['Href']
    return appsessionhref, appsessionparams


def parse_appsessionparams(appsessionparams, arguments_with_content=ARGUMENTS_WITH_CONTENT, arguments_with_items=ARGUMENTS_WITH_ITEMS):

    param_values = {}

    param_values.update(
        {param.get('Name').lower(): param.get('Content')
         for param in appsessionparams
         if param.get('Name').lower() in arguments_with_content
        }
    )
    param_values.update(
        {param.get('Name').lower(): param.get('Items')
         for param in appsessionparams
         if param.get('Name').lower() in arguments_with_items
        }
    )

    # TODO redundant data in the AppSession.json file - ignore ?
    # param_values.update(
    #     {'input.sample_id':
    #         [{'id': sample['Id'], 'href':sample['Href'], 'name': sample['Name']}
    #          for param in appsessionparams
    #          if param.get('Name').lower() == 'input.sample-id'
    #          for sample in param.get('Items')
    #         ]
    #     }
    # )
    # TODO redundant data in the AppSession.json file - but only one project ? -  ignore ?
    param_values.update(
        {'input.project_id': param.get('Content').get('Id')
         for param in appsessionparams
         if param.get('Name').lower() == 'input.project-id'
        }
    )

    param_values.update(
        {'input.samples':
            [{'id': sample['Id'], 'href':sample['Href'], 'name': sample['Name']}
             for param in appsessionparams
             if param.get('Name').lower() == 'input.samples'
             for sample in param.get('Items')
            ]
        }
    )
    param_values.update(
        {'input.projects':
            [{'id': project['Id'], 'href':project['Href'], 'name': project['Name']}
             for param in appsessionparams
             if param.get('Name').lower() == 'input.projects'
             for project in param.get('Items')
            ]
        }
    )
    param_values.update(
        {'output.projects':
            [{'id': project['Id'], 'href':project['Href'], 'name': project['Name']}
             for param in appsessionparams
             if param.get('Name').lower() == 'output.projects'
             for project in param.get('Items')
            ]
        }
    )
    return param_values


metadatatemplate = {
     "Properties": [{"Items": [], "Type": "sample[]", "Name": "Input.Samples"}],
     "Name": "",
     "HrefAppSession": "",
     "Description": ""
}

def json_deepcopy(obj):
    return json.loads(json.dumps(obj))


def write_metadata(name, description, appsessionhref, sampleshrefs, output_dir):
    metadata = json_deepcopy(metadatatemplate)
    metadata['Name'] = name
    metadata['Description'] = description
    metadata['HrefAppSession'] = appsessionhref
    metadata['Properties'][0]['Items'].extend(sampleshrefs)
    print()
    # print('===========\n'
    #       'APP RESULTS\n'
    #       '===========\n')
    print('--------------\n'
          '_metadata.json\n'
          '--------------\n')
    jsonprettystring = json.dumps(metadata, indent=4, sort_keys=True)
    print(jsonprettystring)
    with open(output_dir + '/_metadata.json', 'w') as out:
        out.write(jsonprettystring)
    with open(output_dir + '/metadata.txt', 'w') as out:
         out.write(jsonprettystring)
    print()


def write_results(results, output_dir):
    print('-------------------\n'
          'payload_results.txt\n'
          '-------------------\n')
    print(str(results))
    print()
    with open(output_dir + 'payload_results.txt','w') as out:
        out.write(str(results))


def write_params(param_values, output_dir):
    print('--------------------\n'
          'appsessionparams.csv\n'
          '--------------------\n')
    with open(output_dir + 'appsessionparams.csv','w') as out:
        for key, value in iteritems(param_values):
            line = '%s\t%s' % (key,value)
            if True:   # key != 'input.samples':
                out.write(line)
                print(line)
    print()


def process_appsession(appsessionhref, param_values, data_dir, payloadfunc):

    project_id = param_values.get('input.projects')[0]['id']
    samples = param_values.get('input.samples')
    sampleshrefs = [sample['href'] for sample in samples]

    # for samoutput_dirple in samples:
    #     sample_output_dir = '/data/output/appresults/%s/%s' % (project_id, sample['name'])
    #     os.system('mkdir -p "%s"' % sample_output_dir)
    #     process_sample(sample, sample_output_dir, param_values)
    #     write_sample_metadata(sample['name'], 'Sample Description', appsessionhref, sampleshrefs, sample_output_dir)

    # output_dir = datadir + 'output/appresults/' + str(project_id) + '/sessionsummary_' + datetime.now().isoformat('_') + '/'
    output_dir = data_dir + 'output/appresults/' + str(project_id) + '/sessionsummary/'
    # ATN output_dir gets created by the call to payload     # TODO no longer true?
    os.system('mkdir -p ' + output_dir)
    os.system('mkdir -p ' + data_dir + 'scratch/')
    os.system('mkdir -p ' + data_dir + 'log/')

    ###########################################
    logline_start_time = "process sample starts: " +  datetime.now().isoformat('_') + '\n'
    with open(data_dir + 'log/log.txt', 'a') as handle:
        handle.write(logline_start_time)
    # print(logline_start_time, end ='')

    print("param_values : ")
    print(json.dumps(param_values, indent=4, sort_keys=True))
    results = "Hello BaseSpace App\n"
    # results += globals()[payloadfunc](param_values, data_dir)
    results += payloadfunc(param_values, data_dir)

    # coypy scratch to output_dir, so it is saved as results by basespace
    # copytree(source, destination, ignore=_logpath)
    # copytree(data_dir + 'scratch/', output_dir + '../sessiondetails_' + datetime.now().isoformat('_'))
    copytree(data_dir + 'scratch/', output_dir + '../sessiondetails/')

    logline_end_time = "end process sample ends: " + datetime.now().isoformat('_') + '\n'
    with open(data_dir + 'log/log.txt', 'a') as handle:
        handle.write(logline_end_time)
    # print(logline_end_time, end ='')
    ############################################

    # TODO check why the output_dir is created inside the payload call, then move print metadatqa to before the payload
    write_metadata('sessionsummary','Session Description', appsessionhref, sampleshrefs, output_dir)
    write_params(param_values, output_dir)
    if results:
        write_results(results, output_dir)


# default payload
###################

def default_payload(params_values, data_dir):
    """
    do stuff with data in params_value, saving files into data_dir
    :param params_values:
    :param data_dir:
    :return:
    """
    results = "results default string\n"
    print(results)
    filepath = data_dir + 'scratch/parameters.csv'
    results = '\n'.join([key + ': ' + str(value) for key, value in iteritems(params_values)])
    with open(filepath, 'w') as filehandle:
        filehandle.write(results)
    return results


###################
# MAIN API FUNCTION
###################

def main(datadir='/data/', payloadfunc=default_payload):
    # print("APPSESS", APPSESS )
    # print("datadir + 'input/AppSession.json'" , datadir + 'input/AppSession.json')
    # print("---")
    # print(">>>os.listdir(datadir + 'input/')")
    # print(os.listdir(datadir + 'input/'))
    # print("---")
    # print(">>>os.listdir(datadir)")
    # print(os.listdir(datadir))
    # print("---")


    appsessionhref, appsessionparams = read_appsession(datadir + 'input/AppSession.json')
    param_values = parse_appsessionparams(appsessionparams)
    process_appsession(appsessionhref, param_values, datadir, payloadfunc)


parser = argparse.ArgumentParser(description='app, a sample app to test basespace native app platform')
parser.add_argument('datadir',
                    help='directory path containing input/AppSession.json and input/samples/'
                    )
parser.add_argument('payloadfunc',
                    help='payload python function, should take 2 args: params_values, data_dir'
                    )


# this file executed as script
##############################
if __name__ == '__main__':
    args = parser.parse_args()
    main(args.datadir, args.payloadfunc)
