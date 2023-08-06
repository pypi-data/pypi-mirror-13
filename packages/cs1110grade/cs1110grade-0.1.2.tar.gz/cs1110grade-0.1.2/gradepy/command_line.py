def get_test_func(file, grade_package=None):
    import os
    import imp
    mod_name = os.path.basename(file)[:-3]
    test_name = 'grade_' + mod_name

    try:
        test_mod = getattr(grade_package, test_name)
    except AttributeError:
        try:
            mod_junk = imp.find_module(test_name, '.')
        except ImportError as e:
            print '\nERROR: No testing script found for {}\n'.format(file)
            return None
        test_mod = imp.load_module(test_name, *mod_junk)
    print('FOO')
    return test_mod.main

def command_line(test_func=None, grade_package=None):
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Tests student python modules.')
    parser.add_argument('files', nargs='+', metavar='file',
                        help='paths to student modules.')

    args = parser.parse_args()
    for file in args.files:
        test = test_func or get_test_func(file, grade_package=grade_package)
        if test:
            test(file)
