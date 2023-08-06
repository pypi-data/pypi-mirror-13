# -*- coding: UTF-8 -*-
# Copyright 2016 by Luc Saffre & Hamza Khchine.
# License: BSD, see LICENSE for more details.

""""""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from invoke import Collection
from atelier import invlib
from unipath import Path

ns = Collection()
tasks = ns.from_module(invlib)
ns.add_collection(tasks)

def setup_from_tasks(
        globals_dict, main_package=None,
        settings_module_name=None):
    if '__file__' not in globals_dict:
        raise Exception(
            "No '__file__' in %r. "
            "First parameter to must be `globals()`" % globals_dict)

    tasks = Path(globals_dict['__file__'])
    if not tasks.exists():
        raise Exception("No such file: %s" % tasks)
    root_dir = tasks.parent.absolute()
    _globals_dict = dict()
    _globals_dict.update(
        root_dir=root_dir,
        main_package=main_package,
        locale_dir=None,
        tolerate_sphinx_warnings=False,
        demo_projects=[],
        revision_control_system=None,
        apidoc_exclude_pathnames=[],
        project_name=tasks.parent.absolute().name,
        editor_command=None,
        blog_root=root_dir.child('docs'))

    if settings_module_name is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name
        from django.conf import settings
        # why was this? settings.SITE.startup()
        _globals_dict.update(
            languages=[lng.name for lng in settings.SITE.languages])

    _globals_dict.setdefault(
        'build_dir_name', '.build')  # but ablog needs '_build'
    _globals_dict.setdefault('use_dirhtml', False)

    # # The following import will populate the projects
    from atelier.projects import get_project_info_tasks
    prj = get_project_info_tasks(root_dir)
    prj.load_tasks()
    _globals_dict.update(
        current_project=prj, doc_trees=prj.doc_trees)
    # print(globals_dict)
    ns.configure({'main_package':main_package,
                  'doc_trees':prj.doc_trees},)

    ns.configure(_globals_dict)
    return _globals_dict
