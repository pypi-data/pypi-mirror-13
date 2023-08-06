"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  This file is part of the Smart Developer Hub Project:
    http://www.smartdeveloperhub.org

  Center for Open Middleware
        http://www.centeropenmiddleware.com/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2015 Center for Open Middleware.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
"""

from setuptools import setup, find_packages

__author__ = 'Fernando Serena'

setup(
        name="SDH-Curator",
        version="0.1.20",
        author="Fernando Serena",
        author_email="fernando.serena@centeropenmiddleware.com",
        description="The service responsible for supporting resource enrichment on a Linked Data platform",
        license="Apache 2",
        keywords=["linked-data", "ontology", "curation"],
        url="https://github.com/smartdeveloperhub/sdh-curator",
        download_url="https://github.com/smartdeveloperhub/sdh-curator/tarball/0.1.15",
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        namespace_packages=['sdh', 'sdh.curator'],
        install_requires=['shortuuid', 'pika', 'flask', 'Flask-Negotiate', 'redis', 'hiredis', 'APScheduler',
                          'networkx', 'Agora-Client'],
        classifiers=[],
        scripts=['curator'],
        package_dir={'sdh.curator': 'sdh/curator', 'sdh.curator.server': 'sdh/curator/server'},
        package_data={'sdh.curator.server': ['templates/*.*', 'static/*.*']},
)
