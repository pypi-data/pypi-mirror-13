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

        # add parameters to parameters list to catch form fields per tutorial
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.textbox-1':
            parameter = jsonObject['Properties']['Items'][index]['Content']
            parameter_list.append(parameter)
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.numeric-1':
            parameter = jsonObject['Properties']['Items'][index]['Content']
            parameter_list.append(parameter)
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.radio-1':
            parameter = jsonObject['Properties']['Items'][index]['Content']
            parameter_list.append(parameter)
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.checkbox-1':
            parameter = jsonObject['Properties']['Items'][index]['Items'][0]
            parameter_list.append(parameter)

        # add parameters to parameters list to catch dummy fields from test file
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.param1':
            parameter = jsonObject['Properties']['Items'][index]['Content']
            parameter_list.append(parameter)
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.param2':
            parameter = jsonObject['Properties']['Items'][index]['Content']
            parameter_list.append(parameter)
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.param3':
            parameter = jsonObject['Properties']['Items'][index]['Items']
            parameter_list.append(parameter)
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.param4':
            parameter = jsonObject['Properties']['Items'][index]['Items']
            parameter_list.append(parameter)

        # set project ID
        # TODO this now gets id from the first in the list only - what happens if there is more then one in that list ?
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.Projects':
            projectID = jsonObject['Properties']['Items'][index]['Items'][0]['Id']
            parameter_list.append(projectID)

    for index in range(numberOfPropertyItems):
        # set sample parameters
        if jsonObject['Properties']['Items'][index]['Name'] == 'Input.Samples':
            for sampleindex in range(len(jsonObject['Properties']['Items'][index]['Items'])):
                sampleID.append(jsonObject['Properties']['Items'][index]['Items'][sampleindex]['Id'])
                sampleHref.append(jsonObject['Properties']['Items'][index]['Items'][sampleindex]['Href'])
                sampleName.append(jsonObject['Properties']['Items'][index]['Items'][sampleindex]['Name'])

                sampleDir = datadir + 'input/samples/%s/Data/Intensities/BaseCalls' % (sampleID[sampleindex])
                if not os.path.exists(sampleDir):
                    sampleDir = datadir + 'input/samples/%s' % (sampleID[sampleindex])

                # TODO issue with "number of R1 and R2 files do not match" check,
                # for root, dirs, files in os.walk(sampleDir[sampleindex]):
                #     R1files = fnmatch.filter(files, '*_R1_*')
                #     R2files = fnmatch.filter(files, '*_R2_*')
                #     if len(R1files) != len(R2files):
                #         print("number of R1 and R2 files do not match")
                #         sys.exit()

                sampleOutDir = datadir + 'output/appresults/%s/%s' % (projectID, sampleName[sampleindex])
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
                metaJsonObject['Name'] = jsonObject['Properties']['Items'][index]['Items'][sampleindex]['Id']
                metaJsonObject['Description'] = 'Sample Description'
                metaJsonObject['HrefAppSession'] = jsonObject['Href']
                # TODO sampleHref only contains info for samples iterated through so far - bug ?
                for href in sampleHref:
                    metaJsonObject['Properties'][0]['Items'].append(href)

                metaJsonString = json.dumps(metaJsonObject, indent=4, sort_keys=True)

                metadataFile = '%s/_metadata.json' % (sampleOutDir)
                outMetadataFile = open(metadataFile, 'w')
                # json.dump(metaJsonObject, outMetadataFile)
                outMetadataFile.write(metaJsonString)

                metadataFileVisible = '%s/metadata.txt' % (sampleOutDir)
                outMetadataFileVisible = open(metadataFileVisible, 'w')
                # json.dump(metaJsonObject, outMetadataFileVisible)
                outMetadataFileVisible.write(metaJsonString)

parser = argparse.ArgumentParser(description='sampleapp, a sample app to test basespace native app platform')

parser.add_argument('datadir',
                    help='directory path containing input/AppSession.json and samples/'
                    )


# this file executed as script
##############################

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.datadir)
