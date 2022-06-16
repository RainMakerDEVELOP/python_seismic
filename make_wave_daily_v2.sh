#!/bin/bash

if [ "$#" -ne 3 ]; then
    I="/DATA/EQK/RAW1/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00"
    O="/DATA/EQK/RAW1/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00.png"
    T="D"

    echo "INVALID ARG: $#"
    echo "$0 -i -o -t"
    echo "ex) $0 $I $O $T"
    exit 1
fi

EQM_PY_PATH="${EQM_HOME}/bin/image/"
EQM_PY_NAME="img_wave_maker_v2.py"
EQM_PY="${EQM_PY_PATH}${EQM_PY_NAME}"

# * img_wave_maker.py ex)
#   python img_wave_maker.py -fp=/DATA/EQK/RAW1 -o=KMA -j=2019/065 -n=KS -s=SEO2 -c=HHZ -sp=/DATA/EQK/RAW1
# * img_wave_maker_v2.py ex)
#   python img_wave_maker_v2.py -i=/DATA/EQK/RAW1/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00 -o=/DATA/EQM/KS.SEO2.HHZ.2019.020.00.00.00.png -t=D,H


I=$1
O=$2
T=$3

CMD="source ~/.bashrc"
echo $CMD
eval $CMD

CMD="source /opt/anaconda3/anaconda3.env"
echo $CMD
eval $CMD

CMD="conda activate py37"
echo $CMD
eval $CMD

CMD="python ${EQM_PY} -i=${I} -o=${O} -t=${T}"
echo $CMD
eval $CMD

