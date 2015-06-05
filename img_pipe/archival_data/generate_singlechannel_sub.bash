
# Creates the submission file for single channel cleaning.

filename=${1}

cat run_single_channel_clean_header.txt > ${1}

for (( i = 10; i < 215; i++ )); do
    sed -e "s;%ARG%;$i;g" run_single_channel_clean_template.txt >> ${1}
done