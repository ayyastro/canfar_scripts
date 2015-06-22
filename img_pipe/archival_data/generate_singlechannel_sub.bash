
# Creates the submission file for single channel cleaning.

filename=${1}

cat run_single_channel_clean_header.txt > ${1}

for (( i = ${2}; i < $((${3} + 1)); i++ )); do
    sed -e "s;%ARG%;$i;g" run_single_channel_clean_template.txt >> ${1}
done

# Creates separate submission files for each channel
# The other method was causing weird issues that don't seem easy to fix

# file_prefix=${1}

# for (( i = 10; i < 205; i++ )); do
#     cat run_single_channel_clean_header.txt > ${1}_channel_${i}.sub
#     sed -e "s;%ARG%;$i;g" run_single_channel_clean_template.txt >> ${1}_channel_${i}.sub
# done