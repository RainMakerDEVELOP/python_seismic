#!/bin/bash

if [ "$#" -ne 9 ]; then
    FP="/DATA/EQM/ANA/PSD"
    O="KS"
    N="KS"
    S="SEO2"
    C="HHZ"
    L="--"
    SD="20191101"
    ED="20191130"
    SP="/DATA/EQM/ANA/PSD/2019/KS.SEO2.HHZ.201911.png"

    echo "INVALID ARG: $#"
    echo "$0 -fp -o -n -s -c -l -sd -ed -sp"
    echo "ex) $0 $FP $O $N $S $C $L $SD $ED $SP"
    exit 1
fi

EQM_PY_PATH=""
#${EQM_HOME}/bin/image/"
EQM_PY_NAME="/opt/eqm/bin/image/img_psd_maker_fromto.py"
EQM_PY="${EQM_PY_PATH}${EQM_PY_NAME}"

# * img_wave_maker.py ex)
#   python img_wave_maker.py -fp=/DATA/EQK/RAW1 -o=KMA -j=2019/065 -n=KS -s=SEO2 -c=HHZ -sp=/DATA/EQK/RAW1
# * img_wave_maker_v2.py ex)
#   python img_wave_maker_v2.py -i=/DATA/EQK/RAW1/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00 -o=/DATA/EQM/KS.SEO2.HHZ.2019.020.00.00.00.png -t=D,H


FP=$1
O=$2
N=$3
S=$4
C=$5
L=$6
SD=$7
ED=$8
SP=$9

CMD="source ~/.bashrc"
echo $CMD
eval $CMD

CMD="source /opt/anaconda3/anaconda3.env"
echo $CMD
eval $CMD

CMD="conda activate py37"
echo $CMD
eval $CMD

CMD="python ${EQM_PY} -fp=${FP} -o=${O} -n=${N} -s=${S} -c=${C} -l=${L} -sd=${SD} -ed=${ED} -sp=${SP}"
echo $CMD
eval $CMD

