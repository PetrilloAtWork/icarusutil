#!/usr/bin/env python
# ----------------------------------------------------------------------
#
# Name: experiment_utilities.py
#
# Purpose: A python module containing various experiment-specific
#          python utility functions.
#
# Created: 28-Oct-2013  H. Greenlee
#
# ----------------------------------------------------------------------

from __future__ import print_function

import os

# Don't fail (on import) if samweb is not available.

try:
    import samweb_cli
except ImportError:
    pass


def get_dropbox(filename):

    # Get metadata.

    md = {}
    exp = 'icarus'
    if 'SAM_EXPERIMENT' in os.environ:
        exp = os.environ['SAM_EXPERIMENT']
    samweb = samweb_cli.SAMWebClient(experiment=exp)
    try:
        md = samweb.getMetadata(filenameorid=filename)
    except:
        pass

    # Extract the metadata fields that we need.

    file_type = ''
    group = ''
    data_tier = ''

    if 'file_type' in md:
        file_type = md['file_type']
    if 'group' in md:
        group = md['group']
    if 'data_tier' in md:
        data_tier = md['data_tier']

    if not file_type or not group or not data_tier:
        raise RuntimeError(
            'Missing or invalid metadata for file %s.' % filename)

    # Construct dropbox path.

    #path = '/uboone/data/uboonepro/dropbox/%s/%s/%s' % (file_type, group, data_tier)
    if 'FTS_DROPBOX' in os.environ:
        dropbox_root = os.environ['FTS_DROPBOX']
    else:
        dropbox_root = '/pnfs/icarus/scratch/icaruspro/dropbox'
    path = '%s/%s/%s/%s' % (dropbox_root, file_type, group, data_tier)
    return path

# Return fcl configuration for experiment-specific sam metadata.


def get_sam_metadata(project, stage):
    result = ''
    # result = 'services.FileCatalogMetadataICARUS: {\n'
    # if type(stage.fclname) == type('') or type(stage.fclname) == type(u''):
    #     result = result + '  FCLName: "%s"\n' % os.path.basename(stage.fclname)
    # else:
    #     result = result + '  FCLName: "'
    #     for fcl in stage.fclname:
    #         result = result + '%s/' % os.path.basename(fcl)
    #     result = result[:-1]
    #     result = result + '"\n'
    # result = result + '  FCLVersion: "%s"\n' % project.release_tag
    # result = result + '  ProjectName: "%s"\n' % project.name
    # result = result + '  ProjectStage: "%s"\n' % stage.name
    # result = result + '  ProjectVersion: "%s"\n' % project.version
    # result = result + '}\n'
    # if project.release_tag > 'v04_03_03':
    #     result = result + 'services.TFileMetadataICARUS: @local::icarus_tfile_metadata\n'
    # else:
    #     result = result + 'services.TFileMetadataICARUS: {\n'
    #     result = result + '  JSONFileName:          "ana_hist.root.json"\n'
    #     result = result + '  GenerateTFileMetadata: true\n'
    #     result = result + '  dataTier:              "root-tuple"\n'
    #     result = result + '  fileFormat:            "root"\n'
    #     result = result + '}\n'

    return result

# Function to return path to the setup_icarus.sh script


def get_setup_script_path():

    CVMFS_DIR = "/cvmfs/icarus.opensciencegrid.org/products/icarus/"
    ICARUSUTIL_DIR = ''
    if 'ICARUSUTIL_DIR' in os.environ:
        ICARUSUTIL_DIR = os.environ['ICARUSUTIL_DIR'] + '/bin/'

    if os.path.isfile(CVMFS_DIR+"setup_icarus.sh"):
        setup_script = CVMFS_DIR+"setup_icarus.sh"
    elif ICARUSUTIL_DIR != '' and os.path.isfile(ICARUSUTIL_DIR+"setup_icarus.sh"):
        setup_script = ICARUSUTIL_DIR+"setup_icarus.sh"
    else:
        raise RuntimeError("Could not find setup script at "+CVMFS_DIR)

    return setup_script

# Construct dimension string for project, stage.


def dimensions(project, stage, ana=False):

    data_tier = ''
    if ana:
        data_tier = stage.ana_data_tier
    else:
        data_tier = stage.data_tier
    dim = 'file_type %s' % project.file_type
    dim = dim + ' and data_tier %s' % data_tier
    dim = dim + ' and icarus_project.name %s' % project.name
    dim = dim + ' and icarus_project.stage %s' % stage.name
    dim = dim + ' and icarus_project.version %s' % project.version
    if stage.pubs_output:
        first_subrun = True
        for subrun in stage.output_subruns:
            if first_subrun:
                dim = dim + \
                    ' and run_number %d.%d' % (stage.output_run, subrun)
                first_subrun = False

                # Kluge to pick up mc files with wrong run number.

                if stage.output_run > 1 and stage.output_run < 100:
                    dim = dim + ',1.%d' % subrun
            else:
                dim = dim + ',%d.%d' % (stage.output_run, subrun)
    elif project.run_number != 0:
        dim = dim + ' and run_number %d' % project.run_number
    dim = dim + ' and availability: anylocation'

    return dim


# Status check before submitting batch jobs.

class MetaDataKey:

    def __init__(self):
        self.expname = "icarus"

    def metadataList(self):
        return [self.expname + elt for elt in ('ProjectName', 'ProjectStage', 'ProjectVersion')]

    def translateKey(self, key):
        prefix = key[:2]
        stem = key[2:]
        projNoun = stem.split("Project")
        return prefix + "_Project." + projNoun[1]
