#!/bin/env python

########################################################################################################################
#
# APP
#
# API functions:
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
from datetime import datetime
from .payload import payload
from .config import APPSESS, ARGUMENTS_WITH_CONTENT, ARGUMENTS_WITH_ITEMS


def read_appsession(appsession_jsonfilename):
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

    param_values.update(
        {'input.project_id': param.get('Content').get('Id')
         for param in appsessionparams
         if param.get('Name') == 'Input.project_id'
        }
    )
    param_values.update(
        {'input.projects_ids': project.get('Id')
         for param in appsessionparams
         if param.get('Name') == 'Input.Projects'
         for project in param['Items']
        }
    )
    param_values.update(
        {'output.projects_ids': project.get('Id')
         for param in appsessionparams
         if param.get('Name') == 'Output.Projects'
         for project in param.get('Items')
        }
    )
    param_values.update(
        {'input.samples':
            [{'id': sample['Id'], 'href':sample['Href'], 'name': sample['Name']}
             for param in appsessionparams
             if param.get('Name') == 'Input.Samples'
             for sample in param.get('Items')
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
    with open(output_dir + '/payload_results.txt','w') as out:
        out.write(str(results))


def write_params(param_values, output_dir):
    print('--------------------\n'
          'appsessionparams.csv\n'
          '--------------------\n')
    with open(output_dir + '/appsessionparams.csv','w') as out:
        for key, value in iteritems(param_values):
            line = '%s\t%s\n' % (key,value)
            if key != 'input.samples':
                out.write(line)
                print(line)
    print()


def process_appsession(appsessionhref, param_values, datadir):

    project_id = param_values.get('input.project_id')
    samples = param_values.get('input.samples')
    sampleshrefs = [sample['href'] for sample in samples]

    # for samoutput_dirple in samples:
    #     sample_output_dir = '/data/output/appresults/%s/%s' % (project_id, sample['name'])
    #     os.system('mkdir -p "%s"' % sample_output_dir)
    #     process_sample(sample, sample_output_dir, param_values)
    #     write_sample_metadata(sample['name'], 'Sample Description', appsessionhref, sampleshrefs, sample_output_dir)

    output_dir = datadir + 'output/appresults/' + project_id + '/sessionsummary_' + datetime.now().isoformat('_') + '/'
    scratch_dir = datadir + "scratch/"
    # ATN output_dir gets created by the call to payload     # TODO no longer true?
    os.system('mkdir -p "%s"' % output_dir)
    os.system('mkdir -p "%s"' % scratch_dir)

    ###########################################
    print("process sample starts: ",  datetime.now().isoformat('_'))
    print("param_values : ", param_values)
    results = payload(param_values, output_dir, scratch_dir)
    print("end process sample ends: ",  datetime.now().isoformat('_'))
    ############################################

    # TODO check why the output_dir is created inside the payload call, then move print metadatqa to before the payload
    write_metadata('\nsessionsummary','Session Description', appsessionhref, sampleshrefs, output_dir)
    write_params(param_values, output_dir)
    if results:
        write_results(results, output_dir)


###################
# MAIN API FUNCTION
###################


def main(datadir='/data/'):
    print("APPSESS", APPSESS )
    print("datadir + 'input/AppSession.json'" , datadir + 'input/AppSession.json')
    print()
    # print("type(APPSESS)", type(APPSESS))
    # assert(APPSESS == datadir + 'input/AppSession.json')

    print(">>>os.listdir(datadir + 'input/AppSession.json')")
    print()
    print(os.listdir(datadir + 'input/'))
    print()
    print(os.listdir(datadir))

    appsessionhref, appsessionparams = read_appsession(datadir + 'input/AppSession.json')
    param_values = parse_appsessionparams(appsessionparams)

    # appsessionhref, appsessionparams = read_appsession(APPSESS)
    # param_values = parse_appsessionparams(appsessionparams)

    process_appsession(appsessionhref, param_values, datadir)


parser = argparse.ArgumentParser(description='app, a sample app to test basespace native app platform')

parser.add_argument('datadir',
                    help='directory path containing input/AppSession.json and samples/'
                    )


# this file executed as script
##############################

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.datadir)
