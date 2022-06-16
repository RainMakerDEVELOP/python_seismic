import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import argparse as argp
from scipy.stats import kde
import matplotlib.dates as mdates
# from obspy.imaging.cm import viridis
# from obspy.imaging.cm import pqlx
import datetime as dt
import sys
import re
import time
import copy
import math

fPixelPerInchVal = 0.026458333 * 0.393701
nDpiVal = 96
grp_cnt = 5

# 테스트용 스크립트
#python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/PSD_KS.SEO2.HGZ.2019.323.00.00.00.hour.bin -ii=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/hour.idx -o=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/KS.SEO2.HHZ.2019.020.00.00.00.png -j=323
# python img_psd_maker.py -ib=D:/Project/EQM/DATA/Y2019/HOUR/H020.bin -ii=D:/Project/EQM/DATA/Y2019/HOUR/hour.idx -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.020.00.00.00.png -j=020
#python img_psd_maker.py -i=D:/Project/EQM/DATA/Y2019/HOUR -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.020.00.00.00.png -j=020
#python img_psd_maker.py -fp=D:\Project\EQM\DATA\Y2019/HOUR -o=KMA -y=2019 -j=020 -n=KS -s=SEO2 -c=HHZ -sp=D:\Project\EQM\DATA -it=day -gc=5
#python img_psd_maker.py --filepath=D:\Project\EQM\DATA\Y2019/HOUR --org=KMA --jday=2019/065 --net=* --sta=* --chn=* --savepath=D:\Project\EQM\DATA --interval_type=day --grp_cnt=5

def Split_Data(data, sep) :
    arr = []

    if data :
        arr = data.split(sep)
        # if data.find(sep) >= 0 :
        #     arr = data.split(sep)
        # else :
        #     arr = data.split()
    
    return arr

def GetArraySize(data) :
    size = data.__len__()

    if size == 1 :
        if len(data[0]) == 0 :
            size = 0
    
    return size

def GetDirectoryList(chk_path) :
    dir_lst = ""

    current_path = os.getcwd()
    os.chdir(chk_path)
    dir_lst = [chk_path for chk_path in os.listdir('.') if os.path.isdir(chk_path)]

    # print(os.getcwd())
    # print(chk_path)

    os.chdir(current_path)
    return dir_lst

def GetFileList(chk_path) :
    file_lst = []

    # current_path = os.getcwd()
    # os.chdir(chk_path)
    file_lst = os.listdir(chk_path)
    file_lst = [file for file in file_lst if file.endswith(".00.00.00")]    

    # os.chdir(current_path)
    # print(file_lst)
    return file_lst

def UpdateFileList(file_lst, chk_type, chk_value) :
    if file_lst :
        for file_lst_idx in range(GetArraySize(file_lst) - 1, -1, -1) :
            chk_data = Split_Data(file_lst[file_lst_idx], ".")

            if chk_data :
                if chk_type == "net" :
                    if not chk_value == chk_data[0] :
                        del file_lst[file_lst_idx]
                        # print(file_lst)
                elif chk_type == "sta" :
                    if not chk_value == chk_data[1] :
                        del file_lst[file_lst_idx]
                        # print(file_lst)
                elif chk_type == "chn" :
                    chk_data_chn = Split_Data(chk_data[2], "_")
                    # print("chk_data[2] = " + chk_data[2] + " , chk_data_chn[0] = " + str(chk_data_chn[0]))
                    if not chk_value == chk_data_chn[0] :
                        del file_lst[file_lst_idx]
                        # print(file_lst)
                elif chk_type == "loc" :
                    chk_data_loc = Split_Data(chk_data[2], "_")
                    #print("chk_data[2] = " + chk_data[2] + " , GetArraySize(chk_data_loc) = " + str(GetArraySize(chk_data_loc)))
                    if chk_value == "None" :    ### loc 가 없는 데이터 처리
                        if not GetArraySize(chk_data_loc) == 1 :
                            del file_lst[file_lst_idx]
                    else :
                        if GetArraySize(chk_data_loc) == 2 :
                            if not chk_value == chk_data_loc[1] :
                                del file_lst[file_lst_idx]
                        else :
                            del file_lst[file_lst_idx]                        
                    # print(file_lst)


    return file_lst

def findFile(root_path, filename) :
    retFileName = ""

    # for (path, dirname, files) in os.walk(root_path) :
    for (path, files) in os.walk(root_path) :
        for f in files :
            findname = path + '/' + f
            if findname == filename :
                retFileName = findname
                break

    return retFileName

def createDirectory(directory) :
    try:
        if not os.path.exists(directory) :
            os.makedirs(directory)
    except OSError :
        print('Error: Creating directory : ' + directory)

def removeFile(file) :
    try:
        if os.path.isfile(file) :
            os.remove(file)
    except OSError :
        print('Error: Remove File : ' + file)

def Proc_PDF_Noise(input_file, output_file, jday) :
    ### 상대 경로를 절대 경로로 변환
    sModulePath = os.getcwd()
    sModulePath = sModulePath.replace('\\\\', '/')
    sModulePath = sModulePath.replace('\\', '/')

    if input_file[0] != '/' and ( input_file[1] != ':' and input_file[2] != '/' ) :
        input_file = sModulePath + "/" + input_file

    ### 저장 파일 경로 설정
    output_file_arr = Split_Data(output_file, '/')

    saveFileName = ""
    savePath = ""

    for output_file_arr_num in range(0, GetArraySize(output_file_arr)) :
        if output_file_arr_num == GetArraySize(output_file_arr) - 1 :
            saveFileName = output_file_arr[output_file_arr_num]
        else :
            savePath += output_file_arr[output_file_arr_num] + "/"

    ### 이미지 저장 경로 확인(없으면 생성)
    createDirectory(savePath)

    ### 타이틀, 파일명용 문자열 생성
    title = saveFileName.upper().replace(".PNG", "")

    saveFileName = savePath + "PDF_Noise_" + title + ".png"

    title = "PDF Noise (" + title + ")"

    ### 기존 파일 삭제
    removeFile(saveFileName)

    # ### JulianDay -> Normal DateTime
    # full_jday = [year, jday_split]
    # day = int(full_jday[1])
    # date = dt.datetime(int(full_jday[0]), 1, 1) + dt.timedelta(day - 1)
    # date_split = Split_Data(date.strftime('%Y/%m/%d'), "/")

    ### PDF Low,High Noise 데이터 처리
    openHourFileFullPath = input_file# + "/hour.idx"
    timeArrayData_tmp = []
    timeArrayData = []

    input_file_stat = os.path.getsize(openHourFileFullPath)

    if input_file_stat <= 0 :
        print("Proc_PDF_Noise : input file size = ", input_file_stat)
        return

    with open(openHourFileFullPath, 'r') as timedata :        
        timelines = timedata.read()

    timeArrayData_tmp = timelines.split('\n')
    
    # print(len(timeArrayData_tmp))
    # sys.exit()

    for i in range(0, len(timeArrayData_tmp)) :
        tmpArrayData = timeArrayData_tmp[i].split(' ')#.replace(' ', '')
        # print(len(tmpArrayData))

        for y in range(len(tmpArrayData) - 1, 0, -1) :
            # print(y, tmpArrayData)
            if tmpArrayData[y] == '' :
                tmpArrayData.remove(tmpArrayData[y])

        if tmpArrayData[0] != '' and float(tmpArrayData[0]) <= 100.0 :
            timeArrayData.append(tmpArrayData)

    # print(timeArrayData)
    # sys.exit()

    ### max, min
    for i in range(0, len(timeArrayData)) :
        if( i == 0 ) :
            max = float(timeArrayData[i][1])
            min = float(timeArrayData[i][1])

            if float(timeArrayData[i][2]) > max :
                max = float(timeArrayData[i][2])
            if float(timeArrayData[i][2]) < min :
                min = float(timeArrayData[i][2])
        else :
            if( float(timeArrayData[i][1]) > max ) :
                max = float(timeArrayData[i][1])
            if( float(timeArrayData[i][1]) < min ) :
                min = float(timeArrayData[i][1])
            if float(timeArrayData[i][2]) > max :
                max = float(timeArrayData[i][2])
            if float(timeArrayData[i][2]) < min :
                min = float(timeArrayData[i][2])

    # print("max = " + str(max))
    # print("min = " + str(min))
    max = round(max + 0.5)
    min = round(min - 0.5)
    # print("max = " + str(max))
    # print("min = " + str(min))

    xpix = 470 * fPixelPerInchVal * 2
    ypix = 400 * fPixelPerInchVal * 2

    fig = plt.figure(figsize=(xpix, ypix), dpi=nDpiVal)
    # fig = plt.figure(figsize=(8,5), dpi=100)
    ax = fig.add_subplot(1,1,1)

    ### grid 눈금 dash 로 표출
    # ax.grid('on', linestyle='--', linewidth=0.5)#, alpha=1)

    # ymax = max + 50# ((max - min) * 1.1)
    # ymin = min - 50# ((max - min) * 1.1)
    ymax = -50
    ymin = -200

    plt.ylim(ymin, ymax)
    # plt.grid(True, linestyle='--', linewidth=0.1)
    # ax.grid('off', linestyle='--')
    ax.set_ylim(ymin, ymax)#[min - 10, max + 10])
    yticks = np.arange(ymin, ymax + 1)

    ytick = []

    for ytick_cnt in range(0, len(yticks)) :
        # print(yticks[ytick_cnt])
        if ytick_cnt == 0 :
            ytick.append(yticks[ytick_cnt])
        else :
            if yticks[ytick_cnt] % 10 == 0 :
                ytick.append(yticks[ytick_cnt])

    plt.yticks(yticks)

    # print(ytick)
    # sys.exit()

    ax.set_yticks(ytick)
    ax.set_yticklabels(ytick)
    yticks = ax.yaxis.get_major_ticks()

    # for index, label in enumerate(ax.get_yaxis().get_ticklabels()) :
    #     yticks[index].set_visible(True)
        # if index == 0 :
        #     yticks[index].set_visible(True)
        # else :
        #     if index % 2 != 0 :        
        #         yticks[index].set_visible(False)
        #     else :
        #         yticks[index].set_visible(True)

    # print(freqGroupArrayList[78])

    freqList = []

    ### float 형으로 처리했던 주파수값 리스트를 문자열로 변환 및 자리수 설정
    for i in range(0, len(timeArrayData)) :
        freqList.append(str(timeArrayData[i][0]))
        freqToken = freqList[i].split('.')

        if len(freqToken[0]) == 1 :
            if len(freqList[i]) < 8 :           # 문자열 총 길이가 8자리 미만인 경우
                for j in range(0, 8 - len(freqList[i])) :
                    freqList[i] += '0'            
        elif len(freqToken[0]) == 2 :
            if len(freqList[i]) < 9 :           # 문자열 총 길이가 9자리 미만인 경우
                for j in range(0, 9 - len(freqList[i])) :
                    freqList[i] += '0'

    # print(freqList)
    # sys.exit()

    for i in range(0, len(freqList)) :
        freqList[i] = float(freqList[i])
        freqList[i] = str(freqList[i])
        # print(freqList[i], timeArrayData[i][1])    
    # sys.exit()

    highNoiseData = []
    
    for i in range(0, len(timeArrayData)) :
        highNoiseData.append((float(timeArrayData[i][2])))

    lowNoiseData = []
    
    for i in range(0, len(timeArrayData)) :
        lowNoiseData.append((float(timeArrayData[i][1])))

    # print(highNoiseData)
    # print('\n')
    # print(freqList)
    # sys.exit()

    ### 데이터 역순으로 변환
    freqList.reverse()
    highNoiseData.reverse()
    lowNoiseData.reverse()

    # print(freqList)
    # print(highNoiseData)

    r = 0.0
    g = 0.0
    b = 0.0
    a = 1.0

    xTickList = []
    highNoiseList = []
    lowNoiseList = []
    setTerm = float(freqList[0]) / (len(freqList) / 3)

    for i in range(0, len(highNoiseData)) :
        highNoiseList.append(highNoiseData[i])

    for i in range(0, len(lowNoiseData)) :
        lowNoiseList.append(lowNoiseData[i])

    for i in range(0, len(freqList) / 3) :
        if i == 0 :
            xTickList.append('0')
            # highNoiseList.append('')
        else :
            xTickList.append(str(round(setTerm * i, 6)))
            # highNoiseList.append('')
    
    for i in range(0, len(freqList)) :
        xTickList.append(freqList[i])
        # highNoiseList.append(highNoiseData[i])

    # print(highNoiseData)

    # print(highNoiseData)
    # sys.exit()
    # print(xTickList, highNoiseList)
    # sys.exit()    

    # print(freqList)
    # print('\n')
    # print(xTickList)

    plt.xlim(str(int(float(xTickList[0]))), str(int(float(xTickList[len(xTickList) - 1]))))#xTickList[len(xTickList) - 1])
    plt.xticks(xTickList)

    ### high Noise Plot
    ax.plot(freqList, highNoiseData, zorder=0, linewidth=5, alpha=a, color=(r / 255, g / 255, b / 255))
    # ax.plot(xTickList, highNoiseList, zorder=0, linewidth=2, alpha=a, color=(r / 255, g / 255, b / 255))

    ### low Noise Plot
    ax.plot(freqList, lowNoiseData, zorder=0, linewidth=5, alpha=a, color=(r / 255, g / 255, b / 255))

    # plt.xlim(str(int(float(xTickList[0]))), str(int(float(xTickList[len(xTickList) - 1]))))#xTickList[len(xTickList) - 1])
    # # print(xTickList[0], xTickList[len(xTickList) - 1])
    # # print(xTickList)

    # # for i in range(0, len(xTickList)) :
    # #     xTickList[i] = float(xTickList[i])
    # print(xTickList)
    # plt.xticks(xTickList)

    # plt.gca().invert_yaxis()
    # plt.gca().invert_xaxis()

    # print('\n')
    # print(freqList, highNoiseData)

    for item in [fig, ax] :
        item.patch.set_visible(False)
    # ax.patch.set_visible(False)

    # print(len(timeArrayCnt))
    # sys.exit()

    xticks = ax.xaxis.get_major_ticks()

    nIdx = 1

    ### xtick visible 설정 및 값 변경
    bChk_0 = False
    bChk_01 = False
    bChk_1 = False
    bChk_10 = False
    bChk_100 = False
    nVisible_xticks_0 = 0
    nVisible_xticks_01 = 0
    nVisible_xticks_1 = 0
    nVisible_xticks_10 = 0
    nVisible_xticks_100 = 0

    for i in range(0, len(xTickList)) :
        if i == 0 :
            # print(i)
            xticks[i].set_visible(True)
            bChk_0 = True
        else :
            fChkVal = round(float(xTickList[i]), 1)
            nChkVal = math.trunc(float(xTickList[i]))

            # print(i, fChkVal)

            if fChkVal == 0.1 and bChk_01 == False :
                if fChkVal == round((float(xTickList[i]) - 0.05), 1) :
                    # print(i)
                    xticks[i].set_visible(True)
                    nVisible_xticks_01 = i
                    bChk_01 = True
                else :
                    xticks[i].set_visible(False)
            elif nChkVal == 1 and bChk_1 == False :
                # print(i)
                xticks[i].set_visible(True)
                nVisible_xticks_1 = i
                bChk_1 = True
            elif nChkVal == 10 and bChk_10 == False :
                # print(i)
                xticks[i].set_visible(True)
                nVisible_xticks_10 = i
                bChk_10 = True
            elif nChkVal == 100 and bChk_100 == False :
                # print(i)
                xticks[i].set_visible(True)
                nVisible_xticks_100 = i
                bChk_100 = True
                break
            else:
                xticks[i].set_visible(False)

    labels = [item.get_text() for item in ax.get_xticklabels()]
    labels[nVisible_xticks_0] = '0'
    labels[nVisible_xticks_01] = '0.1'
    labels[nVisible_xticks_1] = '1'
    labels[nVisible_xticks_10] = '10'
    labels[nVisible_xticks_100] = '100'
    ax.set_xticklabels(labels)
    
    # sys.exit()

    # for index, label in enumerate(ax.get_xaxis().get_ticklabels()) :
    #     if index == 0 : # or index == len(timeArrayData) - 1 :
    #         xticks[index].set_visible(True)            
    #         continue

    #     nSize = len(xTickList) - 1    

    #     # print(index, int((float(nSize) / 4) * nIdx))
    #     if index == int((float(nSize) / 4) * nIdx) : #% 100 != 0 : 
    #         xticks[index].set_visible(True)
    #         nIdx += 1
    #     else :
    #         xticks[index].set_visible(False)

    # print(freqList[0], freqList[len(freqList) - 1])

    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    # plt.xlim(freqList[0], freqList[len(freqList) - 1])
    # plt.xlim(xTickList[0], freqList[len(freqList) - 1])#xTickList[len(xTickList) - 1])
    # print(xTickList[0], xTickList[len(xTickList) - 1])
    plt.title(str(title))#, fontsize=8)
    plt.xlabel('Frequency')#, fontsize=8)
    plt.ylabel('Power (dB)')#, fontsize=8)
    # plt.legend(title='Freq. Grp', loc='upper right', fontsize=8, ncol=2)

    # numitems = len(list(ax._get_legend_handles()))
    # print(numitems)

    plt.xticks(rotation=60)
    plt.subplots_adjust(top=0.96, bottom=0.11, left=0.07, right=0.93)
    # print(saveFileName)
    plt.savefig(str(saveFileName))
    # plt.colorbar(sc, label="")

    # plt.show()

def main() :    
    parser = argp.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help="analysis file path")                  # ex) /opt/eqm/data/temp/PDF/M/20191106010000/R/Y2019/HOUR
    # parser.add_argument('-ii', '--inputidx', type=str, help="analysis idx file path")                  # ex) /opt/eqm/data/temp/PDF/M/20191106010000/R/Y2019/HOUR
    parser.add_argument('-o', '--output', type=str, help="analysis result file full path")          # ex) /opt/eqm/data/temp/PDF/M/20191106010000/R/Y2019/HOUR/KS.SEO2.HHZ.00.00.00.png
    parser.add_argument('-j', '--jday', type=str, help="julian day")    # ex) 020

    args = parser.parse_args()
    input_file = args.input
    # input_file_idx = args.inputidx
    output_file = args.output
    jday = args.jday

    Proc_PDF_Noise(input_file, output_file, jday)
    
if __name__ == "__main__" :
    start_time = time.time()
    print(time.strftime("[%y%m%d] START %X", time.localtime()))
    main()

    end_time = time.time()
    print(time.strftime("[%y%m%d] END %X", time.localtime()))
    
    print("processing time : %s sec" %round(end_time - start_time, 4))