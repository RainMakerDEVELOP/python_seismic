#!/bin/bash

if [ "$#" -ne 7 ]; then
    IFP="/opt/eqm/src/qc/pdf_custom/log/test_y2/KS.SEO2..HHZ/T"
    N="KS"
    S="SEO2"
    C="HHZ"
    L="--"
    O="/opt/eqm/src/qc/pdf_custom/log/test_y2/PST_KS.SEO2..HHZ.png"
    T="D"

    echo "INVALID ARG: $#"
    echo "$0 -ifp -n -s -c -l -o -t"
    echo "ex) $0 $IFP $N $S $C $L $O $T"
    exit 1
fi

EQM_PY_PATH="${EQM_HOME}/bin/image/"
EQM_PY_NAME="img_pst_maker_fromto.py"
EQM_PY="${EQM_PY_PATH}${EQM_PY_NAME}"

# * img_wave_maker.py ex)
#   python img_wave_maker.py -fp=/DATA/EQK/RAW1 -o=KMA -j=2019/065 -n=KS -s=SEO2 -c=HHZ -sp=/DATA/EQK/RAW1
# * img_wave_maker_v2.py ex)
#   python img_wave_maker_v2.py -i=/DATA/EQK/RAW1/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00 -o=/DATA/EQM/KS.SEO2.HHZ.2019.020.00.00.00.png -t=D,H


IFP=$1
N=$2
S=$3
C=$4
L=$5
O=$6
T=$7

CMD="source ~/.bashrc"
echo $CMD
eval $CMD

CMD="source /opt/anaconda3/anaconda3.env"
echo $CMD
eval $CMD

CMD="conda activate py37"
echo $CMD
eval $CMD

CMD="python ${EQM_PY} -ifp=${IFP} -n=${N} -s=${S} -c=${C} -l=${L} -o=${O} -t=${T}"
echo $CMD
eval $CMD

