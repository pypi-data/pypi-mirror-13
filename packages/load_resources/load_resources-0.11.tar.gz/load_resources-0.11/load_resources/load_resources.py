import os


def load_resources(path, extensions=[], strip_extensions=True):
    """

    Args:
        path:               (str) The system path of the resources dir to load
        extensions:         (list) The file extensions to load
        strip_extensions:    (bool) Whether or not to strip extensions of the loaded resources from the dict keys

    Returns:
        (dict) Resources in dirs and subdirs

    """

    if not isinstance(extensions, list):
        extensions = [extensions]

    files_dict = {}

    for root, subdirs, files in os.walk(path):
        for file in files:
            name, ext = file.split(os.extsep)

            if not strip_extensions:
                name = file

            if len(extensions) == 0 or ext.lower() in extensions:
                file_path = os.path.join(root, file)
                path_arr = file_path.split(path)[1].split(os.sep)[1:]

                update_dict = files_dict

                for _dir in path_arr[:-1]:
                    update_dict[_dir] = update_dict.get(_dir, {})
                    update_dict = update_dict[_dir]

                update_dict.update({name: open(file_path, 'r').read()})

    return files_dict
