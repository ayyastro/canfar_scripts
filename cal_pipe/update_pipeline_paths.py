
'''
Update EVLA pipeline variables to the current system.
'''


def update_paths(pipe_dict, ms_path, pipepath):

    pipe_dict['ms_active'] = ms_path
    pipe_dict['SDM_name'] = ms_path+".ms"
    pipe_dict['pipepath'] = pipepath

    return pipe_dict


if __name__ == '__main__':

    import sys

    pipe_var_file = str(sys.argv[5])

    ms_path = str(sys.argv[6])

    pipepath = str(sys.argv[7])

    import shelve

    pipe_dict = shelve.open(pipe_var_file, writeback=True)

    pipe_dict = update_paths(pipe_dict, ms_path, pipepath)

    pipe_dict.flush()

    pipe_dict.close()
