# $Id: clean_storage.py 684df47bfce5 2015/03/24 18:26:06 Patrick $
"""Generator script."""

from os import walk
from os.path import join, getmtime, relpath
from time import time
import re

from publiforge.lib.utils import _


EXCLUDED_FILES = ('.hg', '.svn', '.git')


# =============================================================================
def main(processor):
    """Remove somes files from a storage according to a regular expression.

    :param processor: (Processor object)
        Processor object.
    """
    # Get storage handler, ttl and file_regex
    build = processor.build
    storage_id = build.processing['variables'].get('storage')
    if not storage_id:
        build.stopped(_('Storage ID is missing.'))
        return
    handler = processor.storage_handler(storage_id)
    if handler is None:
        return
    ttl = int(build.processing['variables'].get('ttl'))
    file_regex = processor.config('Cleanup', 'file_regex')
    if not file_regex:
        processor.error(_('[Cleanup]/file_regex option is missing.'))
        return
    file_regex = re.compile(file_regex)

    # Find files to remove
    filenames = []
    now = time()
    storage_root = join(build.data_path, storage_id)
    for path, dirs, files in walk(storage_root):
        for name in dirs:
            if name in EXCLUDED_FILES:
                dirs.remove(name)
            elif file_regex.search(name) and \
                    getmtime(join(path, name)) + ttl < now:
                filenames.append(relpath(join(path, name), storage_root))
                dirs.remove(name)
        for name in files:
            if file_regex.search(name) and \
               getmtime(join(path, name)) + ttl < now:
                filenames.append(relpath(join(path, name), storage_root))

    # Remove files
    if not filenames:
        return
    handler[0].remove(
        handler[1], '.', filenames, build.translate(_('Automatic cleaning')))
    for name in filenames:
        processor.message(_('${f} removed', {'f': name}))
