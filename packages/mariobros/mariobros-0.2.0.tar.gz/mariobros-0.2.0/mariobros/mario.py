# -*- coding: utf-8 -*-

# python 2 support via python-future
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import dict, int, str, super

import atexit
import collections
import logging
import re
import subprocess
import uuid

import future.utils
import luigi
import mako.template


LOGGER = logging.getLogger('luigi-interface')

TEMPLATE = """% for var_def, val_def in default_namespace.items():
    % if var_def not in ['action_template', 'sources_repls', 'target_pattern']:
${var_def} = ${val_def}
    %endif
% endfor

% if default_namespace['target_pattern']:
${default_namespace['target_pattern']}: ${default_namespace['sources_repls']}
    ${default_namespace['action_template']}
% endif
% for task_name, section_namespace in section_namespaces.items():
    % if task_name != 'DEFAULT':
[${task_name}]
        %for var, val in section_namespaces[task_name].items():
            % if var not in ['action_template', 'sources_repls', 'target_pattern']:
${var} = ${val}
            % endif
        % endfor
${section_namespace['target_pattern']}: ${section_namespace['sources_repls']}
    ${section_namespace['action_template']}
    % endif

% endfor
"""


class TupleOfStr(tuple):
    """A tuple with a special str representation to be used in rules."""

    def __str__(self):
        return ' '.join(str(item) for item in self)

    def __getitem__(self, key):
        value = super(TupleOfStr, self).__getitem__(key)
        if isinstance(key, slice):
            value = self.__class__(value)
        return value

    def __getslice__(self, i, j):
        value = super(TupleOfStr, self).__getslice__(i, j)
        return self.__class__(value)


class ExistingFile(luigi.ExternalTask):
    """Define Luigi External Task class for existing files requires."""

    target = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.target)


class ReRuleTask(luigi.Task):
    """Define Luigi task class through regular expression.
    """
    # target_pattern = ''
    # sources_repls = []

    # action_namespace = {}
    # action_template = ''

    @staticmethod
    def factory(
            name, target_pattern, sources_repls=(), action_template='', action_namespace={},
            priority=0, worker_timeout=None, resources={}, disabled=False, dry_run_suffix=''):
        """Create Luigi task class.

        :param str name: Task name.
        :param str target_pattern: Target pattern.
        :param list sources_repls: List of source replacements.
        :param str action_template: Action template.
        :param dict action_namespace: Action namespace.
        :param int priority: Priority Luigi task metadata.
        :param int worker_timeout: Worker timeout Luigi task metadata.
        :param dict resources: Resources Luigi task metadata.
        :param bool disabled: Disabled Luigi task metadata.
        :param unicode dry_run_suffix: Suffix to be added to file created during dry run.
        :rtype: subclass_of_ReRuleTask
        """
        # FIXME: move class init code to init method?
        if not target_pattern.startswith('(?<![^/])'):
            target_pattern = '(?<![^/])' + target_pattern
        if not target_pattern.endswith('$'):
            target_pattern += '$'
        if action_template.strip() == '':
            action_template = 'echo "${sources} -> ${target}"'
        _target_pattern = re.compile(target_pattern)
        return type(future.utils.native_str(name), (ReRuleTask,), locals())

    @classmethod
    def match(cls, target):
        return bool(cls._target_pattern.search(target))

    target = luigi.Parameter()

    def render_sources(self):
        return TupleOfStr(
                self._target_pattern.sub(repl, self.target) for repl in self.sources_repls
        )

    def render_action(self):
        sources = self.render_sources()
        match = self._target_pattern.match(self.target)
        target_namespace = dict(TARGET=self.target, SOURCES=sources, MATCH=match)
        return render_template(
                self.action_template, target_namespace, default_namespace=self.action_namespace
        )

    def output(self):
        return luigi.LocalTarget(self.target + self.dry_run_suffix)

    def requires(self):
        required = []
        for source in self.render_sources():
            for task_rule in ReRuleTask.__subclasses__():
                if task_rule.match(source):
                    required.append(task_rule(target=source))
                    break
            else:
                required.append(ExistingFile(source))
        return required

    def run(self):
        cmd = self.render_action()
        if self.dry_run_suffix:
            # log intended command line but touch the dry_run target instead
            LOGGER.info(cmd)
            cmd = 'touch ' + self.target + self.dry_run_suffix
            # register the dry_run target removal at program exit
            atexit.register(self.remove_dry_run_file)
        cmd = ['/bin/bash', '-c', cmd]
        LOGGER.info('COMMAND: {}'.format(cmd))
        subprocess.check_call(cmd)

    def remove_dry_run_file(self):
        subprocess.call('rm -f ' + self.target + self.dry_run_suffix, shell=True)


def render_template(template, local_namespace, default_namespace={}):
    """Return the rendered template merging local and default namespaces.

    :param unicode template: Template.
    :param dict local_namespace: Local namespace.
    :param dict default_namespace: Default namespace.
    :rtype: str
    """
    namespace = default_namespace.copy()
    namespace.update(local_namespace)
    return mako.template.Template(template, strict_undefined=True).render(**namespace)


def render_namespace(namespace, default_namespace={}, skip_names=('action_template',)):
    """Return Render section namespaces with default section namespaces also.

    :param dict namespace: Section namespace.
    :param dict default_namespace: default section namespace.
    :param list skip_names: Namespace names to skip in the render process.
    :rtype: dict
    """
    torender_namespace = {k: v for k, v in namespace.items() if k not in skip_names}
    rendered_namespace = {k: v for k, v in namespace.items() if k in skip_names}
    while len(torender_namespace):
        loop = True
        for key, value_template in list(torender_namespace.items()):
            try:
                value = render_template(value_template, rendered_namespace, default_namespace)
                torender_namespace.pop(key)
                rendered_namespace[key] = value
                loop = False
            except NameError:
                pass
        if loop:
            raise NameError("Can't render: {!r}".format(torender_namespace))
    return collections.OrderedDict((k, rendered_namespace[k]) for k in namespace)


def register_tasks(namespaces, default_namespace={}, dry_run_suffix=''):
    """Return a Luigi task class after parsed Luigi task metadata.

    :param dict namespaces: Task namespaces.
    :param dict default_namespace: Default namespaces.
    :param unicode dry_run_suffix: Suffix to be added to file created during dry run.
    :rtype: iterable
    """

    for task_name, namespace in namespaces.items():
        action_namespace = default_namespace.copy()
        action_namespace.update(namespace)
        task_namespace = {
            k: namespace[k] for k in ['target_pattern', 'sources_repls', 'action_template']
            if k in namespace}
        task_namespace['sources_repls'] = task_namespace['sources_repls'].split()
        # luigi attributes
        task_namespace['resources'] = {k.partition('_')[2]: int(v) for k, v in namespace.items()
                                       if k.startswith('resources_')}
        task_namespace.update(
            {k: int(namespace[k]) for k in ['priority', 'disabled', 'worker_timeout']
             if k in namespace})
        yield ReRuleTask.factory(
                task_name, dry_run_suffix=dry_run_suffix, action_namespace=action_namespace,
                **task_namespace
        )


def print_namespaces(default_namespace, section_namespaces):
    """Print namespaces with the Mariofile format.

    :param dict default_namespace: Default namespace dictionary.
    :param dict section_namespaces: Section namespaces dictionary.
    :return: str
    """
    template = mako.template.Template(TEMPLATE)
    namespaces = template.render(
            default_namespace=default_namespace, section_namespaces=section_namespaces
    )
    return namespaces


def render_config(section_namespaces):
    """Parse and render a Mariofile.

    :param dict section_namespaces: Section namespaces dictionary.
    :return: (dict, dict, dict)
    """
    default_namespace = render_namespace(section_namespaces['DEFAULT'])
    rendered_namespaces = collections.OrderedDict(
            (k, render_namespace(v, default_namespace)) for k, v in section_namespaces.items()
    )
    return default_namespace, rendered_namespaces


def mario(rendered_namespaces, default_namespace, targets=('DEFAULT',), dry_run=False):
    """Generate Luigi tasks' file from Mariofile and Luigi template file

    :param dict rendered_namespaces: Rendered namespaces dictionary.
    :param dict default_namespace: Default namespace dictionary.
    :param iterable targets: List of targets.
    :param bool dry_run: Dry run flag.
    :rtype : iterable
    """
    dry_run_suffix = '-dry_run-' + str(uuid.uuid4()) if dry_run else ''
    rendered_namespaces = collections.OrderedDict(reversed(list(rendered_namespaces.items())))
    tasks = list(register_tasks(
            rendered_namespaces, default_namespace=default_namespace, dry_run_suffix=dry_run_suffix
    ))
    target_tasks = []
    for target in targets:
        for task_rule in tasks:
            if task_rule.match(target):
                target_tasks.append(task_rule(target=target))
                break
    return target_tasks
