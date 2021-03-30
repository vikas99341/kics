#!/usr/bin/env python3
import argparse
import glob
import os

YAML = 'yaml'
JSON = 'json'
TF = 'tf'
DOCKERFILE = 'dockerfile'
AWS = 'aws'
AZURE = 'azure'
GCP = 'gcp'

public_clouds = [AWS, AZURE, GCP]

basepath = os.sep.join(['assets', 'queries'])

iac_tool_dict = {
    'ansible': {'path': os.sep.join([basepath, 'ansible']), 'platforms': public_clouds, 'exts': [YAML]},
    'cloudFormation': {'path': os.sep.join([basepath, 'cloudFormation']), 'exts': [JSON, YAML]},
    'common': {'path': os.sep.join([basepath, 'common']), 'exts': [JSON, YAML, TF, DOCKERFILE]},
    'dockerfile': {'path': os.sep.join([basepath, 'dockerfile']), 'exts': [DOCKERFILE]},
    'k8s': {'path': os.sep.join([basepath, 'k8s']), 'exts': [YAML]},
    'terraform': {'path': os.sep.join([basepath, 'terraform']), 'platforms': [*public_clouds, 'github', 'kubernetes', 'kubernetes_pod'], 'exts': [TF]}
}

samples_dict = {}

for key, value in iac_tool_dict.items():
    for ext in value['exts']:
        path = value['path']
        if 'platforms' in value:
            for platform in value['platforms']:
                plat_path = os.sep.join([path, platform])
                samples_dict[f'{key}_{platform}_{ext}'] = glob.glob(os.sep.join(
                    [plat_path, '**', 'test', f'*.{ext}']))
        else:
            samples_dict[f'{key}_{ext}'] = glob.glob(
                os.sep.join([path, '**', 'test', f'*.{ext}']))

for key, value in iac_tool_dict.items():
    print(key)

print('TOTAL SAMPLES', sum([len(sample)
      for key, sample in samples_dict.items()]))
