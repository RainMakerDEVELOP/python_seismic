#!/bin/bash

if [ "$#" -ne 10 ]; then
    IMBP="/DATA/EQK/RAW1/KMA"
    IRBP="/NFS/EQM/DAT/RESP"
    IRF="RESP.KS.SEO2..HHZ"
    O="/DATA/EQM/ANA/KS.SEO2.HHZ..201911.png"
    N="KS"
    S="SEO2"
    C="HHZ"
    L="--"
    SD="20191101"
    ED="20191130"

    echo "INVALID ARG: $#"
    echo "$0 -imbp -irbp -irf -n -s -c -l -sd -ed"
    echo "ex) $0 $FP $IMBP $IRBP $IRF $O $N $S $C $L $SD $ED $SP"
    exit 1
fi

EQM_PY_PATH=""
#${EQM_HOME}/bin/image/"
EQM_PY_NAME="/opt/eqm/bin/image/img_spectrogram_maker_fromto.py"
EQM_PY="${EQM_PY_PATH}${EQM_PY_NAME}"

# * img_wave_maker.py ex)
#   python img_wave_maker.py -fp=/DATA/EQK/RAW1 -o=KMA -j=2019/065 -n=KS -s=SEO2 -c=HHZ -sp=/DATA/EQK/RAW1
# * img_wave_maker_v2.py ex)
#   python img_wave_maker_v2.py -i=/DATA/EQK/RAW1/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00 -o=/DATA/EQM/KS.SEO2.HHZ.2019.020.00.00.00.png -t=D,H


IMBP=$1
IRBP=$2
IRF=$3
O=$4
N=$5
S=$6
C=$7
L=$8
SD=$9
ED=${10}

CMD="source ~/.bashrc"
echo $CMD
eval $CMD

CMD="source /opt/anaconda3/anaconda3.env"
echo $CMD
eval $CMD

CMD="conda activate py37"
echo $CMD
eval $CMD

CMD="python ${EQM_PY} -imbp=${IMBP} -irbp=${IRBP} -irf=${IRF} -o=${O} -n=${N} -s=${S} -c=${C} -l=${L} -sd=${SD} -ed=${ED}"
echo $CMD
eval $CMD

