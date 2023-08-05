########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############


def after_env_create(loader, **kwargs):
    branches_yaml = loader.storage_dir / 'branches.yaml'
    branches_yaml.touch()


def before_init(blueprint, inputs, **kwargs):
    node_templates = blueprint['node_templates']
    repos = inputs.pop('repos', {})
    for repo_name, repo in repos.items():
        repo_node_template_name = '{}-repo'.format(repo_name)
        properties = repo.get('properties', {})
        properties.update({
            'name': repo_name,
            'repo_type': repo.get('type', 'misc')
        })
        node_templates.update({
            repo_node_template_name: {
                'type': 'git_repo',
                'properties': properties,
                'relationships': [{
                    'target': 'repos_dir',
                    'type': 'cloudify.relationships.depends_on'
                }]
            }
        })
        python = repo.get('python', True)
        if not python:
            continue
        elif python is True:
            python = [{
                'name': repo_name
            }]
        elif isinstance(python, dict):
            python = [python]
        for python_package in python:
            package_name = python_package.get('name', repo_name)
            package_node_template_name = '{}-package'.format(package_name)
            node_templates.update({
                package_node_template_name: {
                    'type': 'python_package',
                    'properties': {
                        'name': package_name,
                        'path': python_package.get('path', '')
                    },
                    'relationships': [
                        {'target': repo_node_template_name,
                         'type': 'package_depends_on_repo'},
                        {'target': 'virtualenv',
                         'type': 'package_depends_on_virtualenv'}
                    ]
                }
            })
            dependencies = python_package.get('dependencies', [])
            if (repo.get('type') == 'plugin' and
                    'cloudify-plugins-common' not in dependencies):
                dependencies.append('cloudify-plugins-common')
            for dependency in dependencies:
                relationships = node_templates[package_node_template_name][
                    'relationships']
                relationships.append({
                    'target': '{}-package'.format(dependency),
                    'type': 'package_depends_on_package'
                })
    package_installer = node_templates['package_installer']
    relationships = package_installer['relationships']
    for node_template_name, node_template in node_templates.items():
        if node_template['type'] == 'python_package':
            relationships.append({
                'target': node_template_name,
                'type': 'cloudify.relationships.depends_on'
            })
    docs = node_templates.get('docs.getcloudify.org-repo')
    docs_site = node_templates.get('docs.getcloudify.org-site-repo')
    if docs and docs_site:
        relationships = docs_site['relationships']
        relationships.append({
            'target': 'docs.getcloudify.org-repo',
            'type': 'docs_site_depends_on_docs'
        })
