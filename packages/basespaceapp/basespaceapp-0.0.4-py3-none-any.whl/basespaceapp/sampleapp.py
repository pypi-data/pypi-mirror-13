#!/bin/env python

########################################################################################################################
#
# APP
#
# API functions: main
#
# this is very close to the example gicen in basespace documentation
# intended to be run as a script (if __name__ == '__main__': code)
#
########################################################################################################################

from __future__ import absolute_import, division, print_function        # , unicode_literals
import json
import argparse

import os


def metadatajson():
    json_file = json.dumps(
        {
            "Name": "",
            "Description": "",
            "HrefAppSession": "",
            "Properties": [
                {
                    "Type": "sample[]",
                    "Name": "Input.Samples",
                    "Items": [

                    ]
                }
            ]
        }
    )
    return json_file


# app specific definitions (not needed for personal app)
parameter_list = []
# load json file


###################
# MAIN API FUNCTION
###################


def main(datadir='/data/'):

    jsonfile = open(datadir + 'input/AppSession.json')

    jsonObject = json.load(jsonfile)
    # determine the number of properties
    numberOfPropertyItems = len(jsonObject['Properties']['Items'])
    # loop over properties
    sampleID = []
    sampleHref = []
    sampleName = []
    sampleDir = []
    for index in range(numberOfPropertyItems):
        # add parameters to parameters list
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.textboxtext':
            parameter = jsonObject['Properties']['Items'][index]['Content']
            parameter_list.append(parameter)
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.random-radio':
            parameter = jsonObject['Properties']['Items'][index]['Content']
            parameter_list.append(parameter)
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.checkbox-1':
            parameter = jsonObject['Properties']['Items'][index]['Items'][0]
            parameter_list.append(parameter)
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.circles':
            parameter = jsonObject['Properties']['Items'][index]['Content']
            parameter_list.append(parameter)
        # set project ID
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.Projects':
            projectID = jsonObject['Properties']['Items'][index]['Items'][0]['Id']

    for index in range(numberOfPropertyItems):
        # set sample parameters
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.Samples':
            for sample in range(len(jsonObject['Properties']['Items'][index]['Items'])):
                sampleID.append(jsonObject['Properties']['Items'][index]['Items'][sample]['Id'])
                sampleHref.append(jsonObject['Properties']['Items'][index]['Items'][sample]['Href'])
                sampleName.append(jsonObject['Properties']['Items'][index]['Items'][sample]['Name'])

                sampleDir = datadir + 'input/samples/%s/Data/Intensities/BaseCalls' % (sampleID[sample])
                if not os.path.exists(sampleDir):
                    sampleDir = datadir + 'input/samples/%s' % (sampleID[sample])

                # TODO issue with "number of R1 and R2 files do not match" check,
                # for root, dirs, files in os.walk(sampleDir[sample]):
                #     R1files = fnmatch.filter(files, '*_R1_*')
                #     R2files = fnmatch.filter(files, '*_R2_*')
                #     if len(R1files) != len(R2files):
                #         print("number of R1 and R2 files do not match")
                #         sys.exit()

                sampleOutDir = datadir + 'output/appresults/%s/%s' % (projectID, sampleName[sample])
                os.system('mkdir -p "%s"' % (sampleOutDir))

                # create output file and print parameters to output file (this is where you would run the command)
                ########################################################
                file = '%s/parameters.csv' % (sampleOutDir)
                outFile = open(file, 'w')
                count = 0
                for parameter in parameter_list:
                    count += 1
                    outFile.write('%s,%s\n' % (count, parameter))
                outFile.close()

                # create metadata file for each appresult
                #########################################
                metadataObject = metadatajson()
                metaJsonObject = json.loads(metadataObject)
                # modify metadataObject
                metaJsonObject['Name'] = jsonObject['Properties']['Items'][index]['Items'][sample]['Id']
                metaJsonObject['Description'] = 'Sample Description'
                metaJsonObject['HrefAppSession'] = jsonObject['Href']
                for href in sampleHref:
                    metaJsonObject['Properties'][0]['Items'].append(href)
                metadataFile = '%s/_metadata.json' % (sampleOutDir)
                outMetadataFile = open(metadataFile, 'w')
                json.dump(metaJsonObject, outMetadataFile)


parser = argparse.ArgumentParser(description='sampleapp, a sample app to test basespace native app platform')

parser.add_argument('datadir',
                    help='directory path containing input/AppSession.json and samples/'
                    )


# this file executed as script
##############################

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.datadir)
