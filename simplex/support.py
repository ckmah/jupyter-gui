from os import environ, listdir
from os.path import join, split, isfile, isdir
import json

HOME_DIR = environ['HOME']


def load_config(filepath):
    """

    :param filepath: str; config.txt
    :return:
    """

    config = {}
    with open(filepath) as f:
        for line in f:
            k, v = line.strip().split('=')
            config[k] = v

    print('Simplex configuration:')
    for k, v in sorted(config.items()):
        print('\t{} : {}'.format(k, v))

    return config


def load_libraries(directory_path):
    """

    :param directory_path: str; simplex_data directory
    :return: list; list of library directory paths
    """

    libs = []
    for f in listdir(directory_path):
        fp = join(directory_path, f)
        if isdir(fp):
            libs.append(fp)
    libs = sorted(libs)

    print('SimpleX libraries:')
    for lib in libs:
        print('\t{}'.format(lib))

    return libs


def make_task_json(directory_paths, filepath):
    """

    :param directory_paths: list; list of library directory paths
    :param filepath: str; tasks.json containing all available SimpleX task specifications
    :return: dict; all available SimpleX task specifications
    """

    tasks_by_libraries = {}
    for dp in directory_paths:
        lib = split(dp)[1]

        fp_json = join(dp, '{}.json'.format(lib))
        try:
            tasks = load_json(fp_json)
            tasks_by_libraries.update(tasks)
        except FileNotFoundError:
            raise FileNotFoundError('{} library is missing {}.json.'.format(dp, lib))
        except KeyError:
            raise ValueError('Error loading {}.'.format(fp_json))

    with open(filepath, 'w') as f:
        json.dump(tasks_by_libraries, f, sort_keys=True, indent=2)

    return tasks_by_libraries


def load_json(filepath):
    """

    :param filepath: str; full path to library.json
    :return: None
    """

    print('Loading {} ...'.format(filepath))

    if not isfile(filepath):
        raise FileNotFoundError('The file {} isn\'t found or isn\'t an absolute path.')

    # Open .json
    with open(filepath) as f:
        library = json.load(f)

    processed_tasks = {}

    # Library name
    library_name = library['library_name']

    # Library path
    if 'library_path' in library:  # Use specified library path
        library_path = library['library_path']
        if not library_path.endswith('/'):  # Make sure the library path ends with '/'
            library_path += '/'
            print('\tAppended \'/\' to library_path, which is now: {}.'.format(library_path))
        if not isdir(library_path):  # Use absolute path
            library_path = join(HOME_DIR, library_path)
            print('\tConverted the library path to the absolute path relative to the $HOME directory: {}.'.format(
                library_path))

    else:  # Guess library path
        library_path = join(split(filepath)[0], '')
        print('\tNo library path is specified for {} library so guessed to be {}.'.format(library_name, library_path))

    # Tasks
    tasks = library['tasks']
    for task in tasks:

        # Task label is this task's UID
        label = task['label']
        if label in processed_tasks:
            raise ValueError('Multiple \'{}\' task labels found! Use unique task label for each task.'.format(label))
        else:
            processed_tasks[label] = {}

        processed_tasks[label]['library_path'] = library_path
        processed_tasks[label]['library_name'] = library_name

        # Function name
        processed_tasks[label]['function_name'] = task['function_name']

        # Description
        if 'description' in task:
            processed_tasks[label]['description'] = task['description']
        else:
            processed_tasks[label]['description'] = ''

        # Arguments
        for a in ['required_args', 'optional_args', 'default_args']:
            if a in task:
                required_args = task[a]
                processed_tasks[label][a] = process_args(required_args)
            else:
                processed_tasks[label][a] = []

        # Returns
        if 'returns' in task:
            processed_tasks[label]['returns'] = task['returns']

    return processed_tasks


def process_args(args):
    processed_args = []
    for a in args:
        processed_a = dict()

        processed_a['arg_name'] = a['arg_name']

        if 'default_value' in a:
            processed_a['value'] = a['value']
        else:
            processed_a['value'] = ''

        if 'label' in a:
            processed_a['label'] = a['label']
        else:
            processed_a['label'] = a['arg_name']

        if 'description' in a:
            processed_a['description'] = a['description']
        else:
            processed_a['description'] = ''

        processed_args.append(processed_a)

    return processed_args


def merge_dicts(*dicts):
    """
    Shallow copy and merge dicts into a new dict; precedence goes to
    key value pairs in latter dict.
    :param dicts: iterable of dict;
    :return: dict;
    """

    merged = {}
    for d in dicts:
        merged.update(d)

    return merged


def cast_string_to_int_float_bool_or_str(string):
    """
    Convert string into the following data types (return the first successful):
    int, float, bool, or str.
    :param string: str;
    :return: int, float, bool, or str;
    """

    value = string.strip()

    # try to cast to int or float
    for var_type in [int, float]:
        try:
            converted_var = var_type(value)
            return converted_var
        except ValueError:
            pass

    # try to cast as boolean
    if value == 'True':
        return True
    elif value == 'False':
        return False

    # return as string last priority
    return str(value)