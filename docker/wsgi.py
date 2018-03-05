from mms import mxnet_model_server
import sys
import json
import os
from mms.arg_parser import ArgParser

# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#     http://www.apache.org/licenses/LICENSE-2.0
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
mms_arg_header = 'MMS Argument'
args = []
found_mms_args = 0
config_file = os.environ['MXNET_MODEL_SERVER_CONFIG']
is_gpu_image = os.environ['GPU_IMAGE']


def read_models_from_file():
    """
    This method reads the model's meta-data from a local file. This is used for MMS in
    :return: model's meta-data
    """
    models = json.load(open("/mxnet_model_server/.models"))
    return models


try:
    f = open(config_file)
except IOError as e:
    sys.exit("ERROR: File %s could not be located" % config_file)
else:
    print("INFO: Successfully read config file %s.." % config_file)
    with f:
        try:
            content = f.readlines()
            content = [line.rstrip() for line in content]

            for i, line in enumerate(content):
                line = line.lstrip()
                if line.startswith('#') or line.startswith('$'):
                    continue
                if line.startswith('['):
                    found_mms_args = 1 if mms_arg_header.lower() in line.lower() else 0
                if found_mms_args is 1:
                    if line.startswith('--') and content[i+1] != 'optional':
                        args.append(line)
                        if line.startswith('--model'):
                            args += content[i + 1].split(' ')
                        else:
                            args.append(content[i + 1])
        except Exception as e:
            sys.exit("ERROR: Cannot read the open file.")

if is_gpu_image == 1:
    args.append('--gpu')
    args.append(int(os.environ['gpu_id']))
    os.environ['gpu_id'] = str(int(os.environ['gpu_id']) + 1)

# Extract the model's metadata from the file
models = read_models_from_file()
# Parse the arguments
arguments = ArgParser.extract_args(args)
# Instantiate the MMS object to start the MMS app
server = mxnet_model_server.MMS(args=arguments, models=models)
application = server.create_app()
