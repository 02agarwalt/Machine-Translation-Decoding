#!/bin/bash

file_name="decode_with_reordering_limit_future_cost.py"
script_id="rlfc"
declare -a s_arr=(100)
declare -a k_arr=(30)
declare -a d_arr=(4 6 8 1000)

for s in "${s_arr[@]}"
do
    for k in "${k_arr[@]}"
    do
        for d in "${d_arr[@]}"
        do
            output_file="output_${script_id}_s-${s}_k-${k}_d-${d}.txt"
            python ${file_name} -s ${s} -k ${k} -d ${d} > ${output_file}
            # python compute-model-score < ${output_file}
        done
    done
done

