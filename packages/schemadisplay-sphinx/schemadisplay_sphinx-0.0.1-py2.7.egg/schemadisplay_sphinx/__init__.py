# Copyright 2013 New Dream Network, LLC (DreamHost)
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
from sets import Set
import sys

from sqlalchemy.orm import class_mapper
from sqlalchemy_schemadisplay import create_uml_graph


def builder_inited_handler(app):

    def is_valid_folder(folder, skip_folders):
        if len(folder) == 0:
            return False
        for skip_folder in skip_folders:
            if skip_folder in folder:
                return False
        return True

    skip_folders = ""
    if app.config.model_skip_folders:
        skip_folders = app.config.model_skip_folders.split(",")

    str_model_cls = app.config.model_class_name
    if not str_model_cls:
        return
    __import__(str_model_cls[:str_model_cls.rfind(".")])
    obj = sys.modules[str_model_cls[:str_model_cls.rfind(".")]]
    name = str_model_cls[str_model_cls.rfind(".")+1:]
    model_class = getattr(obj, name)

    app.info("Importing modules")
    cwd = os.getcwd()
    modules = Set()
    for root, directories, filenames in os.walk(cwd):
        for filename in filenames:
            folder = str(root)
            relative_folder = folder.replace(cwd, '')
            if not is_valid_folder(relative_folder, skip_folders):
                continue
            if filename.endswith(".py") and not filename.startswith("__"):
                name = filename[:-3]
                module = "%s.%s" % (relative_folder.replace("/", "."), name)
                modules.add(module[1:])

    for module in modules:
        try:
            __import__(module)
        except Exception:
            pass

    app.info("Getting mappers")
    mappers = []
    for cls in model_class.__subclasses__():
        for attr in cls.__dict__.keys():
            try:
                mappers.append(class_mapper(cls))
            except Exception:
                pass

    app.info("Creating the db schema")
    graph = create_uml_graph(mappers,
                             show_operations=False,
                             show_multiplicity_one=False)
    graph.write_png(app.config.model_schema_filename)


def setup(app):
    app.add_config_value('model_class_name', '', 'html')
    app.add_config_value('model_schema_filename', 'db-schema.png', 'html')
    app.add_config_value('model_skip_folders', '', 'html')
    app.connect('builder-inited', builder_inited_handler)
