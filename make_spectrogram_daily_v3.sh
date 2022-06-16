#!/bin/bash

if [ "$#" -ne 10 ]; then
    I="/DATA/EQK/RAW1/KMA/2019/335/KS.SEO2.HHZ.2019.335.00.00.00"
    O="/DATA/EQK/RAW1/KMA/2019/335/KS.SEO2.HHZ..2019.335.00.00.00.png"
    IRBP="/NFS/EQM/DAT/RESP"
    IRF="RESP.KS.SEO2..HHZ"
    Y="2019"
    J="335"
    N="KS"
    S="SEO2"
    C="HHZ"
    L="--"

    echo "INVALID ARG: $#"
    echo "$0 -i -o -irbp -irf -y -j -n -s -c -l"
    echo "ex) $0 $I $O $IRBP $IRF $Y $J $N $S $C $L"
    exit 1
fi

#QM_PY_PATH="${EQM_HOME}/bin/image/"
EQM_PY_NAME="/opt/eqm/bin/image/img_spectrogram_maker_v3.py"
EQM_PY="${EQM_PY_PATH}${EQM_PY_NAME}"

# * img_spectrogram_maker.py ex)
#   python img_spectrogram_maker.py -fp=/DATA/EQK/RAW1 -o=KMA -y=2019 -j=065 -n=KS -s=SEO2 -c=HHZ -sp=/DATA/EQK/RAW1/KMA/2019/020
# * img_spectrogram_maker_v2.py ex)
#   python img_spectrogram_maker_v2.py -i=/DATA/EQK/RAW1/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00 -o=/DATA/EQK/RAW1/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00.png


I=$1
O=$2
IRBP=$3
IRF=$4
Y=$5
J=$6
N=$7
S=$8
C=$9
L=${10}

CMD="source ~/.bashrc"
echo $CMD
eval $CMD

CMD="source /opt/anaconda3/anaconda3.env"
echo $CMD
eval $CMD

CMD="conda activate py37"
echo $CMD
eval $CMD

CMD="python ${EQM_PY} -i=${I} -o=${O} -irbp=${IRBP} -irf=${IRF} -y=${Y} -j=${J} -n=${N} -s=${S} -c=${C} -l=${L}"
echo $CMD
eval $CMD

