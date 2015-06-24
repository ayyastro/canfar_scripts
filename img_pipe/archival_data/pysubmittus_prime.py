
'''
Auto submits jobs and regulates the number that can be run at once.
'''

import os
import sys
import subprocess
import glob
import warnings
import datetime


def can_submit(sub_file, vm_name="ewk_casa_6_19",
               flavor="126e8ef0-b816-43ed-bd5f-b1d4e16fdda0"):
    '''
    Call to submit a job.
    '''
    try:
        subprocess.call(["canfar_submit", sub_file, vm_name, flavor])
        return True
    except Exception, e:
        warnings.warn("The file "+sub_file+" failed to submit with error " + e)
        return False


def exists_and_not_empty(filename):
    if os.path.isfile(filename) and os.path.getsize(filename) > 0:
        return True
    else:
        return False


print("Starting at " + str(datetime.datetime.now()))

max_num = int(sys.argv[1])
path_to_repo = "code_repos/canfar_scripts/img_pipe/archival_data/"

# Grab the individual sub files.
subs = glob.glob(os.path.join(path_to_repo, "single_channel_subs/*.sub"))

# Extract the channel numbers from the sub files.
chan_nums = [sub.split("_")[-1][:-4] for sub in subs]

submitted = []

running = []

current_posn = 0

# Submit the first max_num jobs
for sub in subs[:max_num-1]:
    if can_submit(sub):
        print("Submitted : " + str(chan_nums[current_posn]))
        submitted.append(True)
        running.append(chan_nums[current_posn])
    else:
        submitted.append(False)
    current_posn += 1

completed = []
left = list(set(chan_nums) - set(running))

# Now we check if the log files have been written to to determine if a
# job is done.

while len(left) > 0:

    new_running = []

    for chan_run in running:
        output_file = \
            "output_files/output/single_channel_clean_"+str(chan_run)+".out"

        if exists_and_not_empty(output_file):
            print("Channel " + str(chan_run) + " is finished at " +
                  str(datetime.datetime.now()))

            completed.append(chan_run)

            # Now start running the next channel
            if can_submit(subs[current_posn]):
                print("Submitted : " + str(chan_nums[current_posn]))
                submitted.append(True)
                new_running.append(chan_nums[current_posn])
            else:
                submitted.append(False)

            # Delete channel from remaining
            left.remove(chan_nums[current_posn])

            current_posn += 1

    # Update the running channels now.
    running = list(set(running) - set(completed))
    running = running + new_running


print("Finished at " + str(datetime.datetime.now()))
