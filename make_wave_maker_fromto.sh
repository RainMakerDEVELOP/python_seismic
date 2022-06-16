#!/bin/bash

if [ "$#" -ne 7 ]; then
    IBP="/DATA/EQK/RAW1/KMA"
    IYJ="2019/020,2019/021,2019/022"
    N="KS"
    S="SEO2"
    C="HHZ"
    L="--"
    O="/DATA/EQM/KS.SEO2.HHZ.2019.020-2019.022.png"

    echo "INVALID ARG: $#"
    echo "$0 -ibp -iyj -n -s -c -l -o"
    echo "ex) $0 $IBP $IYJ $N $S $C $L $O"
    exit 1
fi

EQM_PY_PATH="${EQM_HOME}/bin/image/"
EQM_PY_NAME="img_wave_maker_fromto.py"
EQM_PY="${EQM_PY_PATH}${EQM_PY_NAME}"

# * img_wave_maker.py ex)
#   python img_wave_maker.py -fp=/DATA/EQK/RAW1 -o=KMA -j=2019/065 -n=KS -s=SEO2 -c=HHZ -sp=/DATA/EQK/RAW1
# * img_wave_maker_v2.py ex)
#   python img_wave_maker_v2.py -i=/DATA/EQK/RAW1/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00 -o=/DATA/EQM/KS.SEO2.HHZ.2019.020.00.00.00.png -t=D,H


IBP=$1
IYJ=$2
N=$3
S=$4
C=$5
L=$6
O=$7

CMD="source ~/.bashrc"
echo $CMD
eval $CMD

CMD="source /opt/anaconda3/anaconda3.env"
echo $CMD
eval $CMD

CMD="conda activate py37"
echo $CMD
eval $CMD

CMD="python ${EQM_PY} -ibp=${IBP} -iyj=${IYJ} -n=${N} -s=${S} -c=${C} -l=${L} -o=${O}"
echo $CMD
eval $CMD

