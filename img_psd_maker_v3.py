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

#python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v3.py -ib=D:/Project/EQM/DATA/temp/PSD/KS/2019/332/KS.SEO2.HHZ.2019.332.00.00.00.hour.bin -ii=D:/Project/EQM/DATA/temp/PSD/KS/2019/332/KS.SEO2.HHZ.2019.332.00.00.00.hour.idx -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.332.00.00.00.png -j=332 -y=2019 -n=KS -s=SEO2 -c=HHZ
#python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/DATA/temp/PSD/KS/2019/332/KS.SEO2.HHZ.2019.332.00.00.00.hour.bin -ii=D:/Project/EQM/DATA/temp/PSD/KS/2019/332/KS.SEO2.HHZ.2019.332.00.00.00.hour.idx -o=C:/Users/winekein/Desktop/KS.SEO2.HHZ.2019.332.00.00.00.png -j=332 -y=2019 -n=KS -s=SEO2 -c=HHZ
# python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/DATA/temp/PSD/KS/2019/320/KS.SEO2.HHZ.2019.320.00.00.00.hour.bin -ii=D:/Project/EQM/DATA/temp/PSD/KS/2019/320/KS.SEO2.HHZ.2019.320.00.00.00.hour.idx -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.320.00.00.00.png -j=320 -y=2019 -n=KS -s=SEO2 -c=HHZ
# python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/DATA/temp/PSD/KS/2019/321/KS.SEO2.HHZ.2019.321.00.00.00.hour.bin -ii=D:/Project/EQM/DATA/temp/PSD/KS/2019/321/KS.SEO2.HHZ.2019.321.00.00.00.hour.idx -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.321.00.00.00.png -j=321 -y=2019 -n=KS -s=SEO2 -c=HHZ
# python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/DATA/temp/PSD/KS/2019/322/KS.SEO2.HHZ.2019.322.00.00.00.hour.bin -ii=D:/Project/EQM/DATA/temp/PSD/KS/2019/322/KS.SEO2.HHZ.2019.322.00.00.00.hour.idx -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.322.00.00.00.png -j=322 -y=2019 -n=KS -s=SEO2 -c=HHZ
# python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/DATA/temp/PSD/KS/2019/323/KS.SEO2.HHZ.2019.323.00.00.00.hour.bin -ii=D:/Project/EQM/DATA/temp/PSD/KS/2019/323/KS.SEO2.HHZ.2019.323.00.00.00.hour.idx -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.323.00.00.00.png -j=323 -y=2019 -n=KS -s=SEO2 -c=HHZ
# python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/DATA/temp/PSD/KS/2019/324/KS.SEO2.HHZ.2019.324.00.00.00.hour.bin -ii=D:/Project/EQM/DATA/temp/PSD/KS/2019/324/KS.SEO2.HHZ.2019.324.00.00.00.hour.idx -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.324.00.00.00.png -j=324 -y=2019 -n=KS -s=SEO2 -c=HHZ
# python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/DATA/temp/PSD/KS/2019/325/KS.SEO2.HHZ.2019.325.00.00.00.hour.bin -ii=D:/Project/EQM/DATA/temp/PSD/KS/2019/325/KS.SEO2.HHZ.2019.325.00.00.00.hour.idx -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.325.00.00.00.png -j=325 -y=2019 -n=KS -s=SEO2 -c=HHZ
# python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/DATA/temp/PSD/KS/2019/326/KS.SEO2.HHZ.2019.326.00.00.00.hour.bin -ii=D:/Project/EQM/DATA/temp/PSD/KS/2019/326/KS.SEO2.HHZ.2019.326.00.00.00.hour.idx -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.326.00.00.00.png -j=326 -y=2019 -n=KS -s=SEO2 -c=HHZ

# 테스트용 스크립트
#python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/PSD/KS/2019/320/KS.SEO2.HHZ.2019.320.00.00.00.hour.bin -ii=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/PSD/KS/2019/320/KS.SEO2.HHZ.2019.320.00.00.00.hour.idx -o=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/PSD/KS.SEO2.HHZ.2019.320.00.00.00.png -j=320 -y=2019 -n=KS -s=SEO2 -c=HHZ
#python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/PSD/PSD_KS.SEO2.HHZ.2019.328.00.00.00.hour.bin -ii=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/PSD/PSD_KS.SEO2.HHZ.2019.328.00.00.00.hour.idx -o=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/PSD/KS.SEO2.HHZ.2019.328.00.00.00.png -j=328
#python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_psd_maker_v2.py -ib=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/PSD_KS.SEO2.HGZ.2019.323.00.00.00.hour.bin -ii=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/hour.idx -o=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/KS.SEO2.HHZ.2019.020.00.00.00.png -j=323
# python img_psd_maker.py -ib=D:/Project/EQM/DATA/Y2019/HOUR/H020.bin -ii=D:/Project/EQM/DATA/Y2019/HOUR/hour.idx -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.020.00.00.00.png -j=020
#python img_psd_maker.py -i=D:/Project/EQM/DATA/Y2019/HOUR -o=D:/Project/EQM/DATA/KS.SEO2.HHZ.2019.020.00.00.00.png -j=020
#python img_psd_maker.py -fp=D:\Project\EQM\DATA\Y2019/HOUR -o=KMA -y=2019 -j=020 -n=KS -s=SEO2 -c=HHZ -sp=D:\Project\EQM\DATA -it=day -gc=5
#python img_psd_maker.py --filepath=D:\Project\EQM\DATA\Y2019/HOUR --org=KMA --jday=2019/065 --net=* --sta=* --chn=* --savepath=D:\Project\EQM\DATA --interval_type=day --grp_cnt=5

def CheckArguments(args) :
    arguments = dict(args._get_kwargs())
    errMsg = ""

    for k, v in arguments.items() :
        if v is None :
            if len(errMsg) <= 0 :
                errMsg = "Not enough Arguments!!!\nCheck Arguments List : "
            else :
                errMsg += ", "

            errMsg += "--" + k

    return errMsg

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

# def Proc_Spectrum(binfilepath, savepath, org, jday_split, net, sta, chn, loc, grouping_cnt, title, fig_size_x, fig_size_y) :
# def Proc_Spectrum() :
# def Proc_Spectrum(orgfilepath, savepath, org, year, jday_split, net, sta, chn, loc, interval_type, grp_cnt) :
def Proc_Spectrum(input_path_bin, input_path_idx, output_file, jday, year, net, sta, chn, loc) :
    grp_cnt = 5

    ### 2020.02.22 가속도 데이터(channel code 두번째값이 'G')인 경우, 0.0073 ~ 0.015 대역은 표출하지 않음
    if len(chn) > 2 :
        tmp_chn = chn.upper()
        if tmp_chn[1] == 'G' :
            grp_cnt = 4
    else :
        print("channel code error : %s" %chn)
        return -1

    ### 주요주파수 대역 하드코딩(2019.11.07)
    arrAmpInterval = [ [0 for x in range(2)] for y in range(grp_cnt) ]

    if grp_cnt == 4 :
        arrAmpInterval[0][0] = 0.12
        arrAmpInterval[0][1] = 0.23
        arrAmpInterval[1][0] = 0.72
        arrAmpInterval[1][1] = 1.4
        arrAmpInterval[2][0] = 3.4
        arrAmpInterval[2][1] = 6.8
        arrAmpInterval[3][0] = 6.8
        arrAmpInterval[3][1] = 100
    else :
        arrAmpInterval[0][0] = 0.0073
        arrAmpInterval[0][1] = 0.015
        arrAmpInterval[1][0] = 0.12
        arrAmpInterval[1][1] = 0.23
        arrAmpInterval[2][0] = 0.72
        arrAmpInterval[2][1] = 1.4
        arrAmpInterval[3][0] = 3.4
        arrAmpInterval[3][1] = 6.8
        arrAmpInterval[4][0] = 6.8
        arrAmpInterval[4][1] = 100

    ### Label 설정
    plot_label = []
    for nLabIdx in range(0, len(arrAmpInterval)) :
        if nLabIdx == len(arrAmpInterval) - 1 :
            plot_label.append(str(arrAmpInterval[nLabIdx][0]) + "~ Hz")
        else :
            plot_label.append(str(arrAmpInterval[nLabIdx][0]) + "~" + str(arrAmpInterval[nLabIdx][1]) + " Hz")

    ### 상대 경로를 절대 경로로 변환
    sModulePath = os.getcwd()
    sModulePath = sModulePath.replace("\\", "/")

    if input_path_bin[0] != '/' and ( input_path_bin[1] != ':' and input_path_bin[2] != '/' ) :
        input_path_bin = sModulePath + "/" + input_path_bin

    if input_path_idx[0] != '/' and ( input_path_idx[1] != ':' and input_path_idx[2] != '/' ) :
        input_path_idx = sModulePath + "/" + input_path_idx
    
    if output_file[0] != '/' and ( output_file[1] != ':' and output_file[2] != '/' ) :
        output_file = sModulePath + "/" + output_file

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

    saveFileName = savePath + "PST_" + title + ".png"

    # title = "Power Spectrum (" + title + ")"
    # print(net, sta, loc, chn)
    title = net + " " + sta + " " + loc + " " + chn + "\n"

    ### 기존 파일 삭제
    removeFile(saveFileName)

    ### 시간 데이터 처리
    openHourFileFullPath = input_path_idx# + "/hour.idx"
    timeArrayData_tmp = []
    timeArrayData = []

    idx_stat = os.path.getsize(openHourFileFullPath)
    # print("Proc_Spectrum : idx file size = ", idx_stat)

    with open(openHourFileFullPath) as timedata :
        timelines = timedata.read()

    timeArrayData_tmp = timelines.split('\n')
    nSegCnt = 0

    for i in range(0, len(timeArrayData_tmp)) :
        tmpArrayData = timeArrayData_tmp[i].replace(' ', '').split('\t')

        bDataInAryYN = False

        for j in range(0, len(timeArrayData)) :
            if tmpArrayData[0] == timeArrayData[j][0] :
                # if tmpArrayData[1] == timeArrayData[j][1] :
                if tmpArrayData[2] == timeArrayData[j][2] :
                    bDataInAryYN = True
                    # print(i, tmpArrayData, timeArrayData[j])
                    break
        
        if bDataInAryYN == False :
            if len(tmpArrayData[0]) <= 0 :
                continue
            
            timeArrayData.append(tmpArrayData)
            nSegCnt += 1
        
        # # 우선 Segment 수가 47개 이상일 수 없으므로 강제 루프 종료(2019.11.07 김학렬)
        # if nSegCnt >= 47 :
        #     break

    # timeArrayData = []

    # with open(openHourFileFullPath) as timedata :
    #     timelines = timedata.read()

    # timeArrayData = timelines.split('\n')

    # for i in range(0, len(timeArrayData)) :
    #     timeArrayData[i] = timeArrayData[i].replace(' ', '').split('\t')

    ### 주파수 데이터 처리
    # openAmpFileFullPath = orgfilepath + "/H" + str(jday_split) + ".bin"
    # openAmpFileFullPath = input_path + "/H" + str(jday) + ".bin"
    openAmpFileFullPath = input_path_bin
    freqReadData = []

    bin_stat = os.path.getsize(openAmpFileFullPath)
    # print("Proc_Spectrum : bin file size = ", bin_stat)

    if idx_stat <= 0 or bin_stat <= 0 :
        print("Proc_Spectrum : Data Error")
        return

    with open(openAmpFileFullPath) as freqdata :
        freqlines = freqdata.read()

    binDataLines_tmp = freqlines.split('\n')
    freqReadData = []

    # freqReadData = freqlines.split('\n')

    for i in range(0, len(binDataLines_tmp)) :
        binDataArr_tmp = binDataLines_tmp[i].replace(' ', '').split('\t')

        if len(binDataArr_tmp[0]) <= 0 :
            continue

        freqReadData.append(binDataArr_tmp)

    # print(timeArrayData)
    # sys.exit()

    # ### 주파수 데이터의 시간 부분을 시간 데이터와 매칭되는 실제 시간으로 치환
    # timeArrayCnt = []
    # nCnt = 0
    # # fileNum = '158'
    # for i in range(0, len(timeArrayData)) :
    #     if( timeArrayData[i][0] == jday ) :
    #         if nCnt == 0 :
    #             timeArrayCnt.append(timeArrayData[i][1])
    #         else :
    #             bDataYN = False
    #             for k in range(0, len(timeArrayCnt) ) :
    #                 if timeArrayCnt[k] == timeArrayData[i][1] :
    #                     bDataYN = True
    #                     break
    #             if bDataYN == False :
    #                 timeArrayCnt.append(timeArrayData[i][1])

    #         for j in range(0, len(freqReadData)) :
    #             if len(freqReadData[j]) <= 0 :
    #                 continue

    #             if float(freqReadData[j][1]) >= 100.0 :
    #                 continue

    #             if( timeArrayData[i][2] == freqReadData[j][0] ) :
    #                 freqReadData[j][0] = timeArrayData[i][1]
    #             else :
    #                 continue
    #     else :
    #         continue

    # print(timeArrayData)
    # print(freqReadData[0])
    # print(freqReadData)
    # sys.exit()

    nSeq = 0
    arr_Hour_Group = [ [0 for x in range(len(timeArrayData))] for y in range(grp_cnt) ]
    group_val = [ 0 for x in range(grp_cnt) ]
    group_val_cnt = [ 0 for x in range(grp_cnt) ]

    for nHourIdx in range(0, len(timeArrayData)) :
        # print(nHourIdx)
        if timeArrayData[nHourIdx][0] != jday :
            print(nHourIdx, timeArrayData[nHourIdx][0], jday)
            continue

        for nBinDataIdx in range(0, len(freqReadData)) :
            if timeArrayData[nHourIdx][2] != freqReadData[nBinDataIdx][0] :
                # if nBinDataIdx == 0 :
                    # print(nHourIdx, timeArrayData[nHourIdx][2], nBinDataIdx, freqReadData[nBinDataIdx][0])
                continue

            # if nHourIdx == 1 :
            #     print(freqReadData[nBinDataIdx][1])

            fFreq = 1 / float(freqReadData[nBinDataIdx][1])
            nDb = int(freqReadData[nBinDataIdx][2])

            if fFreq >= arrAmpInterval[0][0] and fFreq <= arrAmpInterval[0][1] :    # 0.0073 ~ 0.015
                group_val[0] += nDb
                group_val_cnt[0] += 1
            elif fFreq >= arrAmpInterval[1][0] and fFreq <= arrAmpInterval[1][1] :  # 0.12 ~ 0.23
                group_val[1] += nDb
                group_val_cnt[1] += 1
            elif fFreq >= arrAmpInterval[2][0] and fFreq <= arrAmpInterval[2][1] :  # 0.72 ~ 1.4
                group_val[2] += nDb
                group_val_cnt[2] += 1
            elif fFreq >= arrAmpInterval[3][0] and fFreq <= arrAmpInterval[3][1] :  # 3.4 ~ 6.8
                group_val[3] += nDb
                group_val_cnt[3] += 1
            else :
                if grp_cnt > 4 :
                    if fFreq >= arrAmpInterval[4][0] : # and fFreq <= arrAmpInterval[4][1] :  # 6.8 ~
                        group_val[4] += nDb
                        group_val_cnt[4] += 1

        if group_val_cnt[0] > 0 :
            arr_Hour_Group[0][nSeq] = group_val[0] / group_val_cnt[0]
        if group_val_cnt[1] > 0 :
            arr_Hour_Group[1][nSeq] = group_val[1] / group_val_cnt[1]
        if group_val_cnt[2] > 0 :
            arr_Hour_Group[2][nSeq] = group_val[2] / group_val_cnt[2]
        if group_val_cnt[3] > 0 :
            arr_Hour_Group[3][nSeq] = group_val[3] / group_val_cnt[3]
        
        if grp_cnt > 4 :
            if group_val_cnt[4] > 0 :
                arr_Hour_Group[4][nSeq] = group_val[4] / group_val_cnt[4]

        nSeq += 1
        group_val = [ 0 for x in range(grp_cnt) ]
        group_val_cnt = [ 0 for x in range(grp_cnt) ]

    # for i in range(0, len(arr_Hour_Group)) :
    #     print(i, len(arr_Hour_Group[i]))

    arr_Hour = []
    for i in range(0, len(timeArrayData)) :
        if len(timeArrayData[i][1]) <= 0 :
            continue

        arr_Hour.append(timeArrayData[i][1])
    # print(arr_Hour)
    # sys.exit()

    xPix = 537 * fPixelPerInchVal * 2
    yPix = 200 * fPixelPerInchVal * 2

    fig = plt.figure(figsize=(xPix, yPix), dpi=nDpiVal)
    ax = fig.add_subplot(1,1,1)

    ax.grid('on', linestyle='--', linewidth=0.5)#, alpha=1)
    # ymax = max + 50# ((max - min) * 1.1)
    # ymin = min - 50# ((max - min) * 1.1)

    # strLimit = ""

    # if int(ymax) <= 0 :
    #     strLimit = "1"

    #     if len(str(int(ymax))) - 1 == 0 :
    #         strLimit += "00"
    #     else :
    #         for nLimit in range(0, len(str(int(ymax))) - 1) : 
    #             strLimit += "0"

    # # print(ymax, strLimit)
    # nlim = int(strLimit)
    # # print(nlim, ymax / nlim, round((float(ymax) / nlim), 1) * nlim)
    # ymax = int(round((float(ymax) / nlim), 1) * nlim)
    # # print(ymax)

    # if int(ymin) >= 0 :
    #     strLimit = "1"

    #     if len(str(int(ymin))) - 1 == 0 :
    #         strLimit += "00"
    #     else :
    #         for nLimit in range(0, len(str(int(ymin))) - 1) : 
    #             strLimit += "0"

    # nlim = int(strLimit)
    # ymin = int(round((float(ymin) / nlim), 1) * nlim)
    # # print(ymin)

    ymax = -50
    ymin = -210

    plt.ylim(ymin, ymax)
    # plt.grid(True, linestyle='--', linewidth=0.1)
    # ax.grid('off', linestyle='--')
    ax.set_ylim(ymin, ymax)#[min - 10, max + 10])
    yticks = np.arange(ymin, ymax + 1)

    ytick = []

    for ytick_cnt in range(0, len(yticks)) :
        if yticks[ytick_cnt] % 10 == 0 :
            ytick.append(yticks[ytick_cnt])

    # print(ytick)
    # print(yticks)

    plt.yticks(yticks)

    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks)
    yticks = ax.yaxis.get_major_ticks()

    # for index, label in enumerate(ax.get_yaxis().get_ticklabels()) :
    #     if index % 10 != 0 :        
    #         yticks[index].set_visible(False)
    #     else :
    #         yticks[index].set_visible(True)

    # print(len(freqArrayList[0]))
    # print(len(freqArrayList))

    # clr = [ [0 for x in range(len(timeArrayCnt))] for y in range(len(freqArrayList)) ]
    # tmpClr = [ [0 for x in range(2)] for x in range(len(freqArrayList)) ]

    # i = 0
    # for i in range(0, len(freqArrayList[i])) :
    #     for j in range(0, len(freqArrayList)) :
    #         tmpClr[j][0] = freqArrayList[j][i]
    #         tmpClr[j][1] = 0

    #     nSum = 0
    #     j = 0

    #     for j in range(0, len(tmpClr)) :
    #         if tmpClr[j][1] != 0 :
    #             continue

    #         chkVal = tmpClr[j][0]
    #         nSum = 0

    #         k = 0
    #         for k in range(0, len(tmpClr)) :
    #             if chkVal == tmpClr[k][0] :
    #                 nSum += 1
            
    #         k = 0
    #         for k in range(0, len(tmpClr)) :
    #             if chkVal == tmpClr[k][0] :
    #                 tmpClr[k][1] = nSum

    #     # print(tmpClr)

    #     j = 0
    #     for j in range(0, len(clr)) :
    #         # print(j)
    #         # print(str(tmpClr[j][1]) + " , " + str(int((float(tmpClr[j][1]) / len(clr[0])) * 100)) )
    #         clr[j][i] = int((float(tmpClr[j][1]) / len(clr[0])) * 100) * 4

        # print(str(i) + " : " + str(clr[i]))

    # plt.hist2d(time, freqArrayList[0], (20, 20), cmap=plt.cm.jet)
    # plt.colorbar()
    # plt.show()

    # t = []
    # for i in range(0, len(freqArrayList)) :
    #     t.append(np.array(time))
    # x = np.ravel(t, order='C')
    # y = np.ravel(freqArrayList, order='C')

    #len(freqGroupArrayList)

    # for j in range(0, len(arrIntervalNum)) :
    #     if arrIntervalNum[j][0] >= 0 :
    #         print(j, "0", freqList[arrIntervalNum[j][0]])
    #     if arrIntervalNum[j][1] >= 0 :
    #         print(j, "1", freqList[arrIntervalNum[j][1]])
    # print(arrIntervalNum)

    # cmap = plt.cm.get_cmap("rainbow")
    # colors = cmap(np.linspace(0, 1, 7))

    for i in range(0, grp_cnt) :
        # print(arr_Hour)
        # print(arr_Hour_Group[i])
        # print(label[i])
        ax.plot(arr_Hour, arr_Hour_Group[i], label=plot_label[i], zorder=0, linewidth=1, alpha=1)
        # ax.pcolormesh(xi, yi, zi.reshape(xi.shape), cmap=pqlx)
        # sc = ax.scatter(timeArrayCnt, freqArrayList[i], zorder=1, c=clr[i], s=(200 * clr[i]), edgecolor='', marker='.', cmap=pqlx)    

    # print(len(timeArrayCnt))

    for index, label in enumerate(ax.get_yaxis().get_ticklabels()) :
        if index % 10 != 0 :        
            yticks[index].set_visible(False)
        else :
            yticks[index].set_visible(True)

    xticks = ax.xaxis.get_major_ticks()

    nIdx = 1

    for index, label in enumerate(ax.get_xaxis().get_ticklabels()) :
        if index == 0 : # or index == len(timeArrayData) - 1 :
            xticks[index].set_visible(True)
            continue

        nSize = len(arr_Hour) - 1    

        # print(index, int((nSize / 4) * nIdx))
        if index == int((float(nSize) / 4) * nIdx) : #% 100 != 0 : 
            # print(index)
            xticks[index].set_visible(True)
            nIdx += 1
        else :
            xticks[index].set_visible(False)

    ### x축 라벨 시간 표출 강제로 KST 로 변환 START
    arr_KST_Hour = []

    for i in range(0, len(arr_Hour)) :
        nHour = int(arr_Hour[i][:2]) + 9
        nMin = int(arr_Hour[i][3:5])

        if nHour >= 24 :
            nHour = nHour - 24

        dt_hour = dt.time(hour=nHour, minute=nMin)
        # print(dt_hour)
        dt_hour = dt_hour.strftime('%H:%M')
        # print(dt_hour)

        arr_KST_Hour.append(dt_hour)

    labels = [item.get_text() for item in ax.get_xticklabels()]
    # print(labels)

    for i in range(0, len(labels)) :
        labels[i] = arr_KST_Hour[i]
    ax.set_xticklabels(labels)
    ### x축 라벨 시간 표출 강제로 KST 로 변환 END
    
    title += str(len(arr_Hour)) + "PSDs : " + year + ":" + jday + " - " + year + ":" + jday + "\n"
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.xlim(arr_Hour[0], arr_Hour[-1])
    plt.title(str(title), fontsize=15)# 'Spectrum (KS.SEO2.HHZ.2019.021.00.00.00)'
    plt.xlabel('Time (KST)')
    # plt.ylabel('Power (dB)')
    plt.ylabel(r'Power [10log10(m**2/sec**4/Hz)] [dB]')#, fontsize=8)
    leg = plt.legend(loc='lower left', handlelength=0.3, labelspacing=0, columnspacing=1.5, fontsize=8, ncol=5, framealpha=1.0)
    for line in leg.get_lines() :
        line.set_linewidth(2.0)

    # numitems = len(list(ax._get_legend_handles()))
    # print(numitems)

    # plt.xticks(rotation=45)
    plt.subplots_adjust(top=0.81, bottom=0.11, left=0.07, right=0.93)#, left=0.10, right=0.95)
    plt.savefig(str(saveFileName))
    # plt.colorbar(sc, label="")

    # plt.show()
    plt.close()

# def Proc_PSD(binfilepath, savepath, org, jday_split, net, sta, chn, loc, grouping_cnt, title, fig_size_x, fig_size_y) :
# def Proc_PSD() :
# def Proc_PSD(orgfilepath, savepath, org, year, jday_split, net, sta, chn, loc, interval_type, grp_cnt) :
def Proc_PSD(input_path_bin, input_path_idx, output_file, jday, year, net, sta, chn, loc) :
    grp_cnt = 5

    ### 2020.02.22 channel 코드가 가속도 데이터인 경우, 0.0073 ~ 0.015 대역은 표출하지 않음    
    if len(chn) > 2 :
        tmp_chn = chn.upper()
        if tmp_chn[1] == 'G' :
            grp_cnt = 4
    else :
        print("channel code error : %s" %chn)
        return -1

    ### 상대 경로를 절대 경로로 변환
    sModulePath = os.getcwd()
    sModulePath = sModulePath.replace('\\\\', '/')
    sModulePath = sModulePath.replace('\\', '/')

    if input_path_bin[0] != '/' and ( input_path_bin[1] != ':' and input_path_bin[2] != '/' ) :
        input_path_bin = sModulePath + "/" + input_path_bin

    if input_path_idx[0] != '/' and ( input_path_idx[1] != ':' and input_path_idx[2] != '/' ) :
        input_path_idx = sModulePath + "/" + input_path_idx
    
    if output_file[0] != '/' and ( output_file[1] != ':' and output_file[2] != '/' ) :
        output_file = sModulePath + "/" + output_file

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

    saveFileName = savePath + "PSD_" + title + ".png"

    # title = "Power Spectral Density (" + title + ")"
    title = net + " " + sta + " " + loc + " " + chn + "\n"

    ### 기존 파일 삭제
    removeFile(saveFileName)

    # ### JulianDay -> Normal DateTime
    # full_jday = [year, jday_split]
    # day = int(full_jday[1])
    # date = dt.datetime(int(full_jday[0]), 1, 1) + dt.timedelta(day - 1)
    # date_split = Split_Data(date.strftime('%Y/%m/%d'), "/")

    ### 시간 데이터 처리
    openHourFileFullPath = input_path_idx# + "/hour.idx"
    timeArrayData_tmp = []
    timeArrayData = []

    idx_stat = os.path.getsize(openHourFileFullPath)
    # print("Proc_PSD : hour.idx file size = ", idx_stat)

    with open(openHourFileFullPath, 'r') as timedata :        
        timelines = timedata.read()

    timeArrayData_tmp = timelines.split('\n')
    nSegCnt = 0

    for i in range(0, len(timeArrayData_tmp)) :
        tmpArrayData = timeArrayData_tmp[i].replace(' ', '').split('\t')

        bDataInAryYN = False

        for j in range(0, len(timeArrayData)) :
            if tmpArrayData[0] == timeArrayData[j][0] :
                # if tmpArrayData[1] == timeArrayData[j][1] :
                if tmpArrayData[2] == timeArrayData[j][2] :
                    bDataInAryYN = True
                    # print(i, tmpArrayData, timeArrayData[j])
                    break
        
        if bDataInAryYN == False :
            timeArrayData.append(tmpArrayData)
            nSegCnt += 1

        # # 우선 Segment 수가 47개 이상일 수 없으므로 강제 루프 종료(2019.11.07 김학렬)
        # if nSegCnt >= 47 :
        #     break

    # for i in range(0, GetArraySize(timeArrayData)) :
    #     print(str(timeArrayData[i]))
    # print(timeArrayData)
    # print(GetArraySize(timeArrayData))

    ### 주파수 데이터 처리
    # openAmpFileFullPath = orgfilepath + "/H" + str(jday_split) + ".bin"
    #openAmpFileFullPath = input_path + "/H" + str(jday) + ".bin"
    openAmpFileFullPath = input_path_bin
    freqReadData = []

    bin_stat = os.path.getsize(openAmpFileFullPath)
    # print("Proc_PSD : bin file size = ", bin_stat)

    if idx_stat <= 0 or bin_stat <= 0 :
        print("Proc_PSD : Data Error")
        return

    with open(openAmpFileFullPath) as freqdata :
        freqlines = freqdata.read()

    freqReadData = freqlines.split('\n')


    for i in range(0, len(freqReadData)) :
        if len(freqReadData[i]) <= 0 :
            continue

        freqReadData[i] = freqReadData[i].replace(' ', '').split('\t')

    ### 주파수 데이터의 시간 부분을 시간 데이터와 매칭되는 실제 시간으로 치환
    timeArrayCnt = []
    nCnt = 0
    # fileNum = '158'
    for i in range(0, len(timeArrayData)) :
        if( timeArrayData[i][0] == jday ) :
            if nCnt == 0 :
                timeArrayCnt.append(timeArrayData[i][1])
            else :
                bDataYN = False
                for k in range(0, len(timeArrayCnt) ) :
                    if timeArrayCnt[k] == timeArrayData[i][1] :
                        bDataYN = True
                        break
                if bDataYN == False :
                    timeArrayCnt.append(timeArrayData[i][1])

            for j in range(0, len(freqReadData)) :
                if len(freqReadData[j]) <= 0 :
                    continue

                if float(freqReadData[j][1]) > 100.0 :
                    continue

                if( timeArrayData[i][2] == freqReadData[j][0] ) :
                    freqReadData[j][0] = timeArrayData[i][1]
                else :
                    continue
        else :
            continue

    # print(timeArrayCnt)
    # print(len(timeArrayCnt))

    for i in range(0, len(freqReadData) - 1) :
        if( i == 0 ) :
            max = int(freqReadData[i][2])
            min = int(freqReadData[i][2])
        else :
            if( int(freqReadData[i][2]) > max ) :
                max = int(freqReadData[i][2])
            if( int(freqReadData[i][2]) < min ) :
                min = int(freqReadData[i][2])

    # print("max = " + str(max))
    # print("min = " + str(min))

    # time = []

    for i in range(0, len(freqReadData) - 1) :
        freqReadData[i][1] = float(freqReadData[i][1])

    freqList = []

    for i in range(0, len(freqReadData) - 1) :
        if( i == 0 ) :
            freqList.append( freqReadData[i][1] )
        else :
            dataYN = False
            for j in range(0, len(freqList) ) :
                if( freqReadData[i][1] == freqList[j] ) :
                    dataYN = True
                    break
            
            if float(freqReadData[i][1]) > 100.0 :
                continue

            if( dataYN == False ) :
                freqList.append( freqReadData[i][1] )

    freqList = sorted(freqList)
    # print(freqList)
    # sys.exit()

    # fFreqList = []
    
    # for i in range(0, len(freqList)) :
    #     fFreqList.append(float(freqList[i]))

    # print(fFreqList)

    # y = sorted(fFreqList)
    # print(y)

    # freqList = []
    # print(freqList)
    # for i in range(0, len(fFreqList)) :
    #     freqList.append(str(fFreqList[i]))

    # print(freqList)
    # sys.exit()
    ### 주파수 그룹화
    nIdx = 1
    arrIntervalNum = []
    nGroupCnt = int(grp_cnt)

    for i in range(0, len(freqList)) :
        nIndex = int((float(len(freqList)) / nGroupCnt) * nIdx)

        if i == nIndex or i == len(freqList) - 1 :
            arrIntervalNum.append(i)
            nIdx += 1

    arrGroupFreq = []
    fFreqVal = 0.0
    nIdx = 1
    nIntervalSeq = 0
    nCurrentGroupLen = 0

    for i in range(0, len(freqList)) :
        if i < arrIntervalNum[nIntervalSeq] :        
            fFreqVal += float(freqList[i])
            nCurrentGroupLen += 1
        elif i == arrIntervalNum[nIntervalSeq] :
            fFreqVal += float(freqList[i])
            nCurrentGroupLen += 1
            arrGroupFreq.append(round(fFreqVal / float(nCurrentGroupLen), 6))
            fFreqVal = 0.0
            nIntervalSeq += 1
            nIdx += 1
            nCurrentGroupLen = 0

    # print(arrGroupFreq)

    nGroupFreqStrMaxSize = 0

    for i in range(0, len(arrGroupFreq)) :
        if nGroupFreqStrMaxSize < arrGroupFreq[i] :
            nGroupFreqStrMaxSize = len(str(arrGroupFreq[i]))

    for i in range(0, len(arrGroupFreq)) :
        if len(str(arrGroupFreq[i])) < nGroupFreqStrMaxSize :
            for j in range(0, nGroupFreqStrMaxSize - len(str(arrGroupFreq[i]))) :
                arrGroupFreq[i] = str(arrGroupFreq[i]) + "0"

    # print(arrGroupFreq)

    freqArrayList = [ [0 for x in range(len(timeArrayCnt))] for y in range(len(freqList)) ]
    freqGroupArrayList = [ [0 for x in range(len(freqList))] for y in range(len(timeArrayCnt)) ]

    ### 주파수 그룹별 dB값 그룹화

    for i in range(0, len(freqReadData) - 1) :
        for j in range(0, len(freqList)) :            
            if freqReadData[i][1] == freqList[j] :
                for k in range(0, len(timeArrayCnt)) :
                    if freqReadData[i][0] == timeArrayCnt[k] :
                        freqArrayList[j][k] = int(freqReadData[i][2])
                        break

    ### db 값이 0 인 경우, 위치에 따라 앞 또는 뒤의 값으로 설정(테스트)
    # for i in range(0, len(freqArrayList)) :
    #     for j in range(0, len(freqArrayList[i])) :
    #         if j == 0 :
    #             if freqArrayList[i][j] == 0 :
    #                 freqArrayList[i][j] = freqArrayList[i][j + 1]
    #         if freqArrayList[i][j] == 0 :
    #             freqArrayList[i][j] = freqArrayList[i][j - 1]

    # nFreqVal = [ 0 for x in range(len(freqList)) ]
    nIdx = 1
    # nGroupFreqSeq = 0
    nCurrentGroupLen = 0

    for i in range(0, len(freqArrayList)) :
        for j in range(0, len(freqArrayList[i])) :
            freqGroupArrayList[j][i] = freqArrayList[i][j]

    # xpix = 470 * fPixelPerInchVal * 2
    # ypix = 400 * fPixelPerInchVal * 2
    xpix = 607 * fPixelPerInchVal
    ypix = 531 * fPixelPerInchVal

    # plt.rc(usetex = True)
    fig = plt.figure(figsize=(xpix, ypix), dpi=nDpiVal)
    # fig = plt.figure(figsize=(8,5), dpi=100)
    ax = fig.add_subplot(1,1,1)

    ax.grid('on', linestyle='--', linewidth=0.5)#, alpha=1)
    ymax = max + 50# ((max - min) * 1.1)
    ymin = min - 50# ((max - min) * 1.1)

    # print(ymax, ymin)

    strLimit = ""

    if int(ymax) <= 0 :
        strLimit = "1"

        if len(str(int(ymax))) - 1 == 0 :
            strLimit += "00"
        else :
            for nLimit in range(0, len(str(int(ymax))) - 1) : 
                strLimit += "0"

    # print(ymax, strLimit)
    nlim = int(strLimit)
    # print(nlim, ymax / nlim, round((float(ymax) / nlim), 1) * nlim)
    ymax = int(round((float(ymax) / nlim), 1) * nlim)
    # print(ymax)

    if int(ymin) >= 0 :
        strLimit = "1"

        if len(str(int(ymin))) - 1 == 0 :
            strLimit += "00"
        else :
            for nLimit in range(0, len(str(int(ymin))) - 1) : 
                strLimit += "0"

    nlim = int(strLimit)
    ymin = int(round((float(ymin) / nlim), 1) * nlim)
    # print(ymin)
    ymin = -200
    ymax = -50

    plt.ylim(ymin, ymax)
    # plt.grid(True, linestyle='--', linewidth=0.1)
    # ax.grid('off', linestyle='--')
    ax.set_ylim(ymin, ymax)#[min - 10, max + 10])
    yticks = np.arange(ymin, ymax + 1)

    ytick = []

    for ytick_cnt in range(0, len(yticks)) :
        if yticks[ytick_cnt] % 10 == 0 :
            ytick.append(yticks[ytick_cnt])

    # print(ytick)
    # print(yticks)

    plt.yticks(yticks)

    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks)
    yticks = ax.yaxis.get_major_ticks()

    for index, label in enumerate(ax.get_yaxis().get_ticklabels()) :
        if index % 10 != 0 :        
            yticks[index].set_visible(False)
        else :            
            yticks[index].set_visible(True)

    # print(len(freqArrayList[0]))
    # print(len(freqArrayList))

    clr = [ [0 for x in range(len(timeArrayCnt))] for y in range(len(freqArrayList)) ]
    tmpClr = [ [0 for x in range(2)] for x in range(len(freqArrayList)) ]

    i = 0
    for i in range(0, len(freqArrayList[i])) :
        for j in range(0, len(freqArrayList)) :
            tmpClr[j][0] = freqArrayList[j][i]
            tmpClr[j][1] = 0

        nSum = 0
        j = 0

        for j in range(0, len(tmpClr)) :
            if tmpClr[j][1] != 0 :
                continue

            chkVal = tmpClr[j][0]
            nSum = 0

            k = 0
            for k in range(0, len(tmpClr)) :
                if chkVal == tmpClr[k][0] :
                    nSum += 1
            
            k = 0
            for k in range(0, len(tmpClr)) :
                if chkVal == tmpClr[k][0] :
                    tmpClr[k][1] = nSum

        # print(tmpClr)

        j = 0
        for j in range(0, len(clr)) :
            # print(j)
            # print(str(tmpClr[j][1]) + " , " + str(int((float(tmpClr[j][1]) / len(clr[0])) * 100)) )
            clr[j][i] = int((float(tmpClr[j][1]) / len(clr[0])) * 100) * 4

        # print(str(i) + " : " + str(clr[i]))

    # plt.hist2d(time, freqArrayList[0], (20, 20), cmap=plt.cm.jet)
    # plt.colorbar()
    # plt.show()

    # t = []
    # for i in range(0, len(freqArrayList)) :
    #     t.append(np.array(time))
    # x = np.ravel(t, order='C')
    # y = np.ravel(freqArrayList, order='C')

    #len(freqGroupArrayList)

    # print(len(freqList))
    # print(len(freqGroupArrayList[0]))
    # sys.exit()

    r = 0.0
    g = 0.0
    b = 255.00000
    # a = 1.0

    # print(freqGroupArrayList[78])

    ### float 형으로 처리했던 주파수값 리스트를 문자열로 변환 및 자리수 설정
    for i in range(0, len(freqList)) :
        freqList[i] = str(freqList[i])
        freqToken = freqList[i].split('.')

        if len(freqToken[0]) == 1 :
            if len(freqList[i]) < 8 :           # 문자열 총 길이가 8자리 미만인 경우
                for j in range(0, 8 - len(freqList[i])) :
                    freqList[i] += '0'            
        elif len(freqToken[0]) == 2 :
            if len(freqList[i]) < 9 :           # 문자열 총 길이가 9자리 미만인 경우
                for j in range(0, 9 - len(freqList[i])) :
                    freqList[i] += '0'

    # print(freqList, freqGroupArrayList[0])
    # sys.exit()

    for i in range(0, len(freqGroupArrayList)) :    
        # ax.plot(timeArrayCnt, freqGroupArrayList[i], label=arrGroupFreq[i], zorder=0, linewidth=1, alpha=1)
        # g += 2
        # a -= 0.015
        # print(r, g / 255, b/255, a)
        # print(i, freqGroupArrayList[i])

        # if i == 0 or i == 1 :
        #     # print(freqList)
        #     print(freqGroupArrayList[i])
            ax.plot(freqList, freqGroupArrayList[i], zorder=0, linewidth=1, alpha=0.3, color=(r, g / 255, b / 255))
        # ax.pcolormesh(xi, yi, zi.reshape(xi.shape), cmap=pqlx)
        # sc = ax.scatter(timeArrayCnt, freqArrayList[i], zorder=1, c=clr[i], s=(200 * clr[i]), edgecolor='', marker='.', cmap=pqlx)    

    # print(len(timeArrayCnt))

    xticks = ax.xaxis.get_major_ticks()

    nIdx = 1

    ### xtick visible 설정 및 값 변경
    bChk_01 = False
    bChk_1 = False
    bChk_10 = False
    bChk_100 = False
    nVisible_xticks_0 = -1
    nVisible_xticks_01 = -1
    nVisible_xticks_1 = -1
    nVisible_xticks_10 = -1
    nVisible_xticks_100 = -1

    for i in range(0, len(freqList)) :
        # if i == 0 :
        #     # print("0", i)
        #     # xticks[i].set_visible(True)
        #     # bChk_0 = True
        # else :
            fChkVal = round(float(freqList[i]), 1)
            nChkVal = math.trunc(float(freqList[i]))

            # print(i, fChkVal)

            if fChkVal == 0.1 and bChk_01 == False :
                if fChkVal == round((float(freqList[i]) - 0.05), 1) :
                    # print("0.1", i)
                    xticks[i].set_visible(True)
                    nVisible_xticks_01 = i
                    bChk_01 = True
                else :
                    xticks[i].set_visible(False)
            elif nChkVal == 1 and bChk_1 == False :
                # print("1", i)
                xticks[i].set_visible(True)
                nVisible_xticks_1 = i
                bChk_1 = True
            elif nChkVal == 10 and bChk_10 == False :
                # print("10", i)
                xticks[i].set_visible(True)
                nVisible_xticks_10 = i
                bChk_10 = True
            elif nChkVal == 100 and bChk_100 == False :
                # print("100", i)
                xticks[i].set_visible(True)
                nVisible_xticks_100 = i
                bChk_100 = True
                break
            else:
                xticks[i].set_visible(False)

    labels = [item.get_text() for item in ax.get_xticklabels()]

    if nVisible_xticks_0 != -1 :
        labels[nVisible_xticks_0] = '0'
    if nVisible_xticks_01 != -1 :
        labels[nVisible_xticks_01] = '0.1'
    if nVisible_xticks_1 != -1 :        
        labels[nVisible_xticks_1] = '1'
    if nVisible_xticks_10 != -1 :
        labels[nVisible_xticks_10] = '10'
    if nVisible_xticks_100 != -1 :        
        labels[nVisible_xticks_100] = '100'

    ax.set_xticklabels(labels)

    # for index, label in enumerate(ax.get_xaxis().get_ticklabels()) :
    #     if index == 0 : # or index == len(timeArrayData) - 1 :
    #         xticks[index].set_visible(True)
    #         continue

    #     nSize = len(timeArrayCnt) - 1    

    #     # print(index, int((nSize / 4) * nIdx))
    #     if index == int((float(nSize) / 4) * nIdx) : #% 100 != 0 : 
    #         xticks[index].set_visible(True)
    #         nIdx += 1
    #     else :
    #         xticks[index].set_visible(False)

    title += str(len(timeArrayCnt)) + "PSDs : " + year + ":" + jday + " - " + year + ":" + jday + "\n"
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.xlim(freqList[0], freqList[len(freqList) - 1])
    plt.title(str(title), fontsize=15)#, fontsize=8)
    plt.xlabel('Period (sec)')#, fontsize=8)
    plt.ylabel(r'Power [10log10(m**2/sec**4/Hz)] [dB]')#, fontsize=8)
    # plt.legend(title='Freq. Grp', loc='upper right', fontsize=8, ncol=2)

    # numitems = len(list(ax._get_legend_handles()))
    # print(numitems)

    # plt.xticks(rotation=60)
    # plt.subplots_adjust(top=0.825, bottom=0.145, left=0.125, right=0.837)
    plt.subplots_adjust(top=0.822, bottom=0.144, left=0.127, right=0.84)
    # print(saveFileName)
    plt.savefig(str(saveFileName))
    # plt.colorbar(sc, label="")
    # plt.show()
    plt.close()

def main() :
    # nArgvLen = (len(sys.argv) - 1)

    # if nArgvLen < 8 :
    #     print("Not enough Arguments!!! Check execution arguments.")
    #     return

    parser = argp.ArgumentParser()
    parser.add_argument('-ib', '--inputbin', type=str, help="analysis bin file path")                  # ex) /opt/eqm/data/temp/PDF/M/20191106010000/R/Y2019/HOUR
    parser.add_argument('-ii', '--inputidx', type=str, help="analysis idx file path")                  # ex) /opt/eqm/data/temp/PDF/M/20191106010000/R/Y2019/HOUR
    parser.add_argument('-o', '--output', type=str, help="analysis result file full path")          # ex) /opt/eqm/data/temp/PDF/M/20191106010000/R/Y2019/HOUR/KS.SEO2.HHZ.00.00.00.png
    parser.add_argument('-j', '--jday', type=str, help="julian day (ex : 020)")    # ex) 020
    parser.add_argument('-y', '--year', type=str, help="year")   # ex) 2019
    parser.add_argument('-n', '--net', type=str, help="network code")   # ex) KS
    parser.add_argument('-s', '--sta', type=str, help="station code")   # ex) BGDB    
    parser.add_argument('-c', '--chn', type=str, help="channel code")   # ex) HHZ
    parser.add_argument('-l', '--loc', type=str, default="--", help="location code")   # ex) --

    args = parser.parse_args()

    errMsg = CheckArguments(args)

    if len(errMsg) > 0 :
        print(errMsg)
        return
    
    input_file_bin = args.inputbin
    input_file_idx = args.inputidx
    output_file = args.output
    jday = args.jday
    year = args.year
    net = args.net
    sta = args.sta
    chn = args.chn
    loc = args.loc

    if len(loc) <= 0 :
        loc = "--"

    Proc_PSD(input_file_bin, input_file_idx, output_file, jday, year, net, sta, chn, loc)
    Proc_Spectrum(input_file_bin, input_file_idx, output_file, jday, year, net, sta, chn, loc)
    
if __name__ == "__main__" :
    start_time = time.time()
    print(time.strftime("[%y%m%d] START %X", time.localtime()))
    main()

    end_time = time.time()
    print(time.strftime("[%y%m%d] END %X", time.localtime()))
    
    print("processing time : %s sec" %round(end_time - start_time, 4))