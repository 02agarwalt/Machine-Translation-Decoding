#!/bin/bash

file_name="decode_with_adjacent_swap.py"
script_id="as"
declare -a s_arr=(10000 20000 30000)
declare -a k_arr=(10 20 30)

for s in "${s_arr[@]}"
do
    for k in "${k_arr[@]}"
    do
        output_file="output_${script_id}_s-${s}_k-${k}.txt"
        python ${file_name} -s ${s} -k ${k} > ${output_file}
        # python compute-model-score < ${output_file}
    done
done

