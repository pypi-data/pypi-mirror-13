# $Id: packfilling.py 684df47bfce5 2015/03/24 18:26:06 Patrick $
"""Generator script."""

from os import walk
from os.path import join, isfile, relpath
import re

from publiforge.lib.utils import _, EXCLUDED_FILES


# =============================================================================
def main(processor):
    """Fill pack.

    :param processor: (Processor object)
        Processor object.
    """
    build = processor.build
    file_regex = build.processing['variables']['file_regex'] \
        and re.compile(build.processing['variables']['file_regex'])
    resources = [join(build.data_path, k) for k in
                 build.pack['resources'] + build.processing['resources']]
    if not resources:
        build.stopped(_('no available resource'))
        return

    # Look for the file in resource files
    done = set()
    for resource in [k for k in resources if isfile(k)]:
        resources.remove(resource)
        resource = relpath(resource, build.data_path)
        if resource not in done and \
           (not file_regex or file_regex.search(resource)):
            if 'files' not in build.result:
                build.result['files'] = []
            build.result['files'].append(resource)
            done.add(resource)

    # Look for the file in resource directories
    for resource in resources:
        for path, dirs, files in walk(resource):
            for name in dirs:
                if name in EXCLUDED_FILES or '~' in name:
                    dirs.remove(name)
            for name in files:
                name = relpath(join(path, name), build.data_path)
                if name not in done and \
                   (not file_regex or file_regex.search(name)):
                    if 'files' not in build.result:
                        build.result['files'] = []
                    build.result['files'].append(name)
                    done.add(name)

    # Report
    if 'values' not in build.result:
        build.result['values'] = []
    build.result['values'].append(build.translate(
        _('Found files: ${x}', {'x': len(done)})))
