#!/bin/bash

if [ "$#" -ne 9 ]; then
    II="/DATA/EQM/ANA/PSD/KS/2019/335/KS.SEO2.HHZ.2019.335.00.00.00.hour.bin"
    IB="/DATA/EQM/ANA/PSD/KS/2019/335/KS.SEO2.HHZ.2019.335.00.00.00.hour.idx"
    O="/DATA/EQK/RAW1/KMA/2019/335/KS.SEO2.HHZ.2019.335.00.00.00.png"
    J="335"
    Y="2019"
    N="KS"
    S="SEO2"
    C="HHZ"
    L="--"

    echo "INVALID ARG: $#"
    echo "$0 -ii -ib -o -j -y -n -s -c -l"
    echo "ex) $0 $II $IB $O $J $Y $N $S $C $L"
    exit 1
fi

EQM_PY_PATH=""
#${EQM_HOME}/bin/image/"
EQM_PY_NAME="/opt/eqm/bin/image/img_psd_maker_v2.py"
# EQM_PY_NAME="/opt/eqm/bin/image/img_psd_maker_v3.py"
EQM_PY="${EQM_PY_PATH}${EQM_PY_NAME}"

# * img_wave_maker.py ex)
#   python img_wave_maker.py -fp=/DATA/EQK/RAW1 -o=KMA -j=2019/065 -n=KS -s=SEO2 -c=HHZ -sp=/DATA/EQK/RAW1
# * img_wave_maker_v2.py ex)
#   python img_wave_maker_v2.py -i=/DATA/EQK/RAW1/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00 -o=/DATA/EQM/KS.SEO2.HHZ.2019.020.00.00.00.png -t=D,H


IB=$1
II=$2
O=$3
J=$4
Y=$5
N=$6
S=$7
C=$8
L=$9

CMD="source ~/.bashrc"
echo $CMD
eval $CMD

CMD="source /opt/anaconda3/anaconda3.env"
echo $CMD
eval $CMD

CMD="conda activate py37"
echo $CMD
eval $CMD

CMD="python ${EQM_PY} -ib=${IB} -ii=${II} -o=${O} -j=${J} -y=${Y} -n=${N} -s=${S} -c=${C} -l=${L}"
echo $CMD
eval $CMD

