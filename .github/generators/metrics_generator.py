#!/usr/bin/env python3
import argparse
import glob
import json
import os

from jinja2 import Template

YAML = 'yaml'
JSON = 'json'
TF = 'tf'
DOCKERFILE = 'dockerfile'
AWS = 'aws'
AZURE = 'azure'
GCP = 'gcp'

public_clouds = [AWS, AZURE, GCP]

iac_tool_dict = {
    'ansible': {'path': os.sep.join(['assets', 'queries', 'ansible']), 'platforms': public_clouds, 'exts': [YAML]},
    'cloudFormation': {'path': os.sep.join(['assets', 'queries', 'cloudFormation']), 'exts': [JSON, YAML]},
    'common': {'path': os.sep.join(['assets', 'queries', 'common']), 'exts': [JSON, YAML, TF, DOCKERFILE]},
    'dockerfile': {'path': os.sep.join(['assets', 'queries', 'dockerfile']), 'exts': [DOCKERFILE]},
    'k8s': {'path': os.sep.join(['assets', 'queries', 'k8s']), 'exts': [YAML]},
    'terraform': {'path': os.sep.join(['assets', 'queries', 'terraform']), 'platforms': [*public_clouds, 'github', 'kubernetes', 'kubernetes_pod'], 'exts': [TF]}
}

metrics_dict = {}


def init_entry(key, mdict):
    if key not in mdict.keys():
        mdict[key] = {}


def get_samples(plat_glob_path):
    return [sample for sample in glob.iglob(plat_glob_path) if os.path.basename(sample) != 'positive_expected_result.json']


def sample_glob(path, ext):
    return os.sep.join([path, '**', 'test', f'*.{ext}'])


def query_glob(paths):
    return os.sep.join([*paths, '**', '*.rego'])


for iac_tool, value in iac_tool_dict.items():
    path = value['path']
    init_entry(iac_tool, metrics_dict)
    for ext in value['exts']:
        init_entry(iac_tool, metrics_dict)
        if 'platforms' in value:
            for platform in value['platforms']:
                plat_path = os.sep.join([path, platform])
                init_entry(platform, metrics_dict[iac_tool])
                init_entry('samples', metrics_dict[iac_tool][platform])
                init_entry(ext, metrics_dict[iac_tool][platform]['samples'])
                metrics_dict[iac_tool][platform]['samples'][ext] = get_samples(
                    sample_glob(plat_path, ext))
                metrics_dict[iac_tool][platform]['samples'][f"{ext}_count"] = len(
                    metrics_dict[iac_tool][platform]['samples'][ext])
                metrics_dict[iac_tool][platform]['queries'] = glob.glob(
                    query_glob([path, '**']))
                metrics_dict[iac_tool][platform]['queries_count'] = len(
                    metrics_dict[iac_tool][platform]['queries'])
        else:
            init_entry('samples', metrics_dict[iac_tool])
            init_entry(ext, metrics_dict[iac_tool]['samples'])
            metrics_dict[iac_tool]['samples'][ext] = get_samples(
                sample_glob(path, ext))
            metrics_dict[iac_tool]['samples'][f"{ext}_count"] = len(
                metrics_dict[iac_tool]['samples'][ext])
            metrics_dict[iac_tool]['queries'] = glob.glob(query_glob([path]))
            metrics_dict[iac_tool]['queries_count'] = len(
                metrics_dict[iac_tool]['queries'])

print(json.dumps(metrics_dict, indent=2))

# for key, obj in samples_dict.items():
#     print('--', key)
#     for subkey, subobj in obj.items():
#         print('\t---', subkey)
#         for line in json.dumps(subobj, indent=4).splitlines():
#             print('\t\t', line)
