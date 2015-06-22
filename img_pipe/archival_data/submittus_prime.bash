
# Submit all of the submission files!

# for (( i = 10; i < 205; i++ )); do
#     canfar_submit /home/ekoch/code_repos/canfar_scripts/img_pipe/archival_data/single_channel_subs/single_channel_${i}.sub ewk_casa_4_20 126e8ef0-b816-43ed-bd5f-b1d4e16fdda0
# done

# for ((i = 10; i < 30; i++)) do
#     canfar_submit /home/ekoch/code_repos/canfar_scripts/img_pipe/archival_data/single_channel_subs/single_channel_${i}.sub ewk_casa_6_17 126e8ef0-b816-43ed-bd5f-b1d4e16fdda0
# done

# running=$(seq 10 30)
# left=$(seq 31 215)

# #205-30=175
# ii=175

# while [[ $ii -geq 0 ]]; do
#     for chan in $running; do
#         if [[ -s output_files/output/single_channel_clean_${chan}.out ]]; then
#             :
#         else
#             next_chan=$($left[0])
#             canfar_submit /home/ekoch/code_repos/canfar_scripts/img_pipe/archival_data/single_channel_subs/single_channel_${next_chan}.sub ewk_casa_6_17 126e8ef0-b816-43ed-bd5f-b1d4e16fdda0
#             running=( "${running[@]/$chan}" )
#             left=( "${left[@]/$next_chan}" )
#         fi
#     done
# done

# for ((i = 90; i < 92; i++)) do
#     canfar_submit /home/ekoch/code_repos/canfar_scripts/img_pipe/archival_data/single_channel_subs/single_channel_${i}.sub ewk_casa_6_19 126e8ef0-b816-43ed-bd5f-b1d4e16fdda0
# done

running=$(seq 90 92)
left=($(seq 93 96))

ii=4

posn=0

while [[ $ii -ge 0 ]]; do
    for chan in $running; do
        echo $chan
        if [[ -s output_files/output/single_channel_clean_${chan}.out ]]; then
            :
        else
            next_chan=${left[$posn]}
            canfar_submit /home/ekoch/code_repos/canfar_scripts/img_pipe/archival_data/single_channel_subs/single_channel_${next_chan}.sub ewk_casa_6_19 126e8ef0-b816-43ed-bd5f-b1d4e16fdda0
            ii=$(($ii - 1))
            posn=$(($posn + 1))
        fi
    done
done