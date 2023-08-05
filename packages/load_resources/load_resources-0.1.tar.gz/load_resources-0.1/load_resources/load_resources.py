import os


def load_resources(folder, extensions=[], strip_extension=True):
    if not isinstance(extensions, list):
        extensions = [extensions]

    files_dict = {}

    path = os.path.join(os.path.dirname(__file__), folder)
    for root, subdirs, files in os.walk(path):
        for file in files:
            name, ext = file.split(os.extsep)

            if not strip_extension:
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
