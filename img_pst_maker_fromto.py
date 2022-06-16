#!/usr/bin/env python //python 라이브러리 호출
#-*- coding:utf-8 -*- // utf-8로써 코딩

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator, FixedLocator, FixedFormatter, FormatStrFormatter)
import numpy as np
import argparse as argp
from scipy.stats import kde
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import datetime as dt
import sys
import re
import time
import copy
import math
import colorsys
# import pandas

fPixelPerInchVal = 0.026458333 * 0.393701
nDpiVal = 96

# 테스트용 스크립트
# python.exe d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_pst_maker_fromto.py -ifp=D:/Project/EQM/DATA/PST_TEST/test_month -n=KS -s=SEO2 -c=HHZ -o=D:/Project/EQM/DATA/PST_TEST/test_month/test1.png
#python.exe d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_pst_maker_fromt.py -ifp=D:/Project/EQM/DATA/PST_TEST/test_y2 -n=KS -s=SEO2 -c=HHZ -o=D:/Project/EQM/DATA/PST_TEST/test_y2/test3.png

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

def revised_rgb_to_hsv(r, g, b):
    (h, s, v) = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h *= 360
    s *= 100
    v *= 100
    return h, s, v

def juldate(year, month, day):
    jmonth = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    jday = jmonth[month - 1] + day

    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
        if month > 2:
            return jday + 1

    return jday

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

    try :
        os.chdir(chk_path)
        dir_lst = [chk_path for chk_path in os.listdir('.') if os.path.isdir(chk_path)]
    except Exception as err :
        print("GetDirectoryList Error chdir(%s) : code(%s)" % (chk_path, err))
        return "ERR"

    # print(os.getcwd())
    # print(chk_path)

    os.chdir(current_path)
    return dir_lst

# def GetFileList(chk_path) :
#     file_lst = []

#     # current_path = os.getcwd()
#     # os.chdir(chk_path)
#     file_lst = os.listdir(chk_path)
#     file_lst = [file for file in file_lst if file.endswith(".00.00.00")]    

#     # os.chdir(current_path)
#     # print(file_lst)
#     return file_lst

def GetFileList(chk_path, endswith = ".00.00.00") :
    file_lst = []

    if not os.path.isdir(chk_path) :
        return file_lst    

    # current_path = os.getcwd()
    # os.chdir(chk_path)
    file_lst = os.listdir(chk_path)
    file_lst = [file for file in file_lst if file.endswith(endswith)]    

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
    # root_path = root_path.replace("/./", "/")

    for (path, dirname, files) in os.walk(root_path) :
        for f in files :
            if f == filename :
                retFileName = path + "/" + f
                break
            elif filename.find('*') != -1 :
                retFileName = path + "/" + f
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

def months_between(date1,date2):
    if date1>date2:
        date1,date2=date2,date1
    m1=date1.year*12+date1.month
    m2=date2.year*12+date2.month
    months=m2-m1

    if date1.day>date2.day:
        months-=1
    elif date1.day==date2.day:
        seconds1=date1.hour*3600+date1.minute+date1.second
        seconds2=date2.hour*3600+date2.minute+date2.second
        if seconds1>seconds2:
            months-=1
    return months

def Proc_Spectrum(bin_file_arr, hour_idx_fullpath_arr, st_yearjday, ed_yearjday, output_file, net, sta, chn, loc, maketype) :
    # st_yearjday = '2018/242'
    # ed_yearjday = '2019/060'
    ### 2020.02.25 시작일 - 종료일 날짜 간격 계산
    st_date = dt.datetime.strptime(st_yearjday, '%Y/%j')
    ed_date = dt.datetime.strptime(ed_yearjday, '%Y/%j')
    
    nMonths_gap = months_between(st_date, ed_date)
    nDays_gap = (ed_date - st_date).days + 1

    # print("st_date = '%s', ed_date = '%s'" %(str(st_date.date()), str(ed_date.date())))
    # print("Months = '%d', Days = '%d'" %(nMonths_gap, nDays_gap))

    grp_cnt = 5

    ### 2020.02.22 가속도 데이터(channel code 두번째값이 'G')인 경우, 0.0073 ~ 0.015 대역은 표출하지 않음
    if len(chn) >= 2 :
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
    label = []
    for nLabIdx in range(0, len(arrAmpInterval)) :
        if nLabIdx == len(arrAmpInterval) - 1 :
            label.append(str(arrAmpInterval[nLabIdx][0]) + "~ Hz")
        else :
            label.append(str(arrAmpInterval[nLabIdx][0]) + "~" + str(arrAmpInterval[nLabIdx][1]) + " Hz")

    # print(label)
    # return

    nTotBinCnt = len(bin_file_arr)

    ### Year, Jday 매칭 배열 생성
    jday_arr = []
    year_arr = []

    for nIdx in range(0, nTotBinCnt) :
        bin_file_name_split = Split_Data(bin_file_arr[nIdx], "/")

        if len(bin_file_name_split) > 0 :
            org_bin_file_year = bin_file_name_split[len(bin_file_name_split) - 3][1:]
            org_bin_file_name = bin_file_name_split[len(bin_file_name_split) - 1]
            file_name = Split_Data(org_bin_file_name, ".")

            if len(file_name) > 1 :
                year_arr.append(org_bin_file_year)
                jday_arr.append(file_name[0][1:])

    # print(year_arr, jday_arr)
    # return

    ### 저장 파일 경로 설정
    output_file_arr = Split_Data(output_file, '/')

    saveFileName = ""
    savePath = ""

    for output_file_arr_num in range(0, GetArraySize(output_file_arr)) :
        if output_file_arr_num == GetArraySize(output_file_arr) - 1 :
            saveFileName = output_file_arr[output_file_arr_num]
        else :
            savePath += output_file_arr[output_file_arr_num] + "/"

    ### 저장 경로 생성
    createDirectory(savePath)

    ### 타이틀, 파일명용 문자열 생성
    # saveFileName = savePath + "PST_" + saveFileName.upper().replace(".PNG", "") + ".png"

    title = net + "." + sta + "." + loc + "." + chn# + "\n"

    ### 기존 파일 삭제
    removeFile(output_file)

    xPix = 562 * fPixelPerInchVal
    yPix = 512 * fPixelPerInchVal

    # if nTotBinCnt * 32 > 430 :
    #     xPix = ( (nTotBinCnt * 32) + 512 - 430) * fPixelPerInchVal
    #     yPix = xPix

    # fig = plt.figure(figsize=(xPix, yPix), dpi=nDpiVal)
    # ax = fig.add_subplot(1,1,1)
    
    nPlotDayCnt = 1         ### 한번에 그릴 Jday 일수(axes 하나에 표출될 일수 단위) ex) 1주일 단위 = 7, 1달 단위 = Jday -> YYmm 으로 계산하여 산출
    nGridTerm = 1           ### x축 grid 표출 간격
    nTickTerm = 1           ### x축 tick 표출 간격
    nTickLabelTerm = 1      ### x축 tick label 표출 간격
    nMinorTickTerm = 1      ### x축 minor tick 표출 간격
    bCalcFreqAvgYN = False  ### 일 데이터를 주파수 대역별 평균값으로 처리할지, 시간 단위로 처리할지 여부(False = 시간 단위로 처리)
    nRotation = 0           ### x축 tick label 기울기

    ### x축 grid 표출 간격
    if nMonths_gap >= 6 :
        nGridTerm = 30  ### 년월 변환하여 처리하는 것을 고려할 부분
    elif nMonths_gap >= 4 :
        nGridTerm = 14
    elif nMonths_gap >= 1 :
        nGridTerm = 7

    ### x축 tick 표출 간격
    if nMonths_gap >= 6 :
        nTickTerm = 7

    ### 한번에 그릴 Jday 일수, x축 tick Label 표출 간격
    if nMonths_gap >= 6 :
        nPlotDayCnt = 30    ### 년월 변환하여 처리하는 것을 고려할 부분
        nTickLabelTerm = 30 ### 년월 변환하여 처리하는 것을 고려할 부분
        nMinorTickTerm = 7
    elif nMonths_gap >= 4 :
        nPlotDayCnt = 14    ### 년월 변환하여 처리하는 것을 고려할 부분
        nTickLabelTerm = 14 ### 년월 변환하여 처리하는 것을 고려할 부분        
    elif nMonths_gap >= 1 :
        nPlotDayCnt = 7
        nTickLabelTerm = 7

    ### 일 데이터를 주파수 대역별 평균값으로 처리할지, 시간 단위로 처리할지 여부(False = 시간 단위로 처리)
    if nMonths_gap >= 1 :
        bCalcFreqAvgYN = True

    ### tick label 기울기
    if nMonths_gap < 1 :
        nRotation = 90
    # elif nTotBinCnt <= 120 :
    #     nRotation = 45
    else :
        nRotation = 45

    # print("nTotBinCnt = %d, nPlotDayCnt = %d, nGridTerm = %d, nTickTerm = %d, nTickLabelTerm = %d, nRotation = %d, bCalcFreqAvgYN = %s"\
    #      %(nTotBinCnt, nPlotDayCnt, nGridTerm, nTickTerm, nTickLabelTerm, nRotation, bCalcFreqAvgYN))
    # return -1

    gs_figsize = []

    if bCalcFreqAvgYN == True :
        gs_figsize.append(nTotBinCnt)
    else :
        for i in range(1, nTotBinCnt + 1) :
            # print(nPlotDayCnt, i)
            if i % nPlotDayCnt == 0 :
                gs_figsize.append(nPlotDayCnt)

        if nTotBinCnt % nPlotDayCnt != 0 :
            gs_figsize.append(nTotBinCnt % nPlotDayCnt)

    # print(gs_figsize)
    # return

    fig = plt.figure(1, figsize=(xPix, yPix), dpi=nDpiVal, constrained_layout=True)
    gs = gridspec.GridSpec(1, len(gs_figsize), width_ratios=gs_figsize)
    axs = [fig.add_subplot(ss) for ss in gs]

    # return
    
    nShareIdx = 0

    # for i in range(1, len(axs)) :
    #     if i == 0 :
    #         nShareIdx = i
    #     elif i % nPlotDayCnt == 0 :
    #         nShareIdx = i

    #     if nShareIdx == i :
    #         continue

    #     axs[nShareIdx].get_shared_x_axes().join(axs[nShareIdx], axs[i])

    x_mid = (fig.subplotpars.right + fig.subplotpars.left) / 2
    # print(fig.subplotpars.left)
    # return

    fig.suptitle(title, fontsize=14, fontweight='bold', x=x_mid + 0.05)
    # fig.suptitle("test22", fontsize=8)    

    ### hour.idx 데이터 읽기
    timeArrayData_tmp = []
    timeArrayData = []

    tmp_timelines = []
    timelines = ""

    for i in range(0, len(hour_idx_fullpath_arr)) :
        with open(hour_idx_fullpath_arr[i]) as timedata :
            tmp_timelines = timedata.read()

        # print(i, tmp_timelines)

        if len(tmp_timelines) > 0 :
            timelines += tmp_timelines
            
            # for j in range(0, len(tmp_timelines)) :
            #     if len(tmp_timelines[j]) > 0 :
            #         timelines.append(tmp_timelines[j])
            #     else :
            #         print("len(timelines[j]) <= 0")
            #         continue

    # print(timelines)
    # return

    timeArrayData_tmp = timelines.split('\n')
    nTotSegCnt = 0

    for i in range(0, len(timeArrayData_tmp)) :
        tmpArrayData = timeArrayData_tmp[i].replace(' ', '').split('\t')

        if len(tmpArrayData[0]) <= 0 :
            continue

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
            nTotSegCnt += 1

    nCombineCnt = 0
    nAxesCombineNum = 0
    nAxesPlotTotDataCnt = 0
    arr_Hour_Jday_Group_tmp = []
    arr_Hour_Group_tmp = [[] for y in range(grp_cnt)]
    nHourJdayGroupCount = 0
    arrXTickPos = []
    bLastLabelSetYN = False
    nLastLabelIdx = 0
    arrDayAvgVal = [ [0 for x in range(5)] for y in range(gs_figsize[nAxesCombineNum]) ]
    arrDayAvgVal_pv = [ [0 for x in range(gs_figsize[nAxesCombineNum])] for y in range(5) ]
    arrDayNum = [ x for x in range(gs_figsize[nAxesCombineNum])]
    # print(arr_Hour_Group_tmp)
    # return

    jday_arr_int = list(map(int, jday_arr))
    nPrevVal = 0
    nCurVal = 0

    for nJdayNum in range(0, len(jday_arr_int)) :
        if nJdayNum == 0 :
            nPrevVal = jday_arr_int[nJdayNum]
            continue

        nCurVal = jday_arr_int[nJdayNum]

        if nPrevVal > nCurVal :
            jday_arr_int[nJdayNum] = jday_arr_int[nJdayNum] + 365

        nPrevVal = jday_arr_int[nJdayNum]

    # print(jday_arr_int)
    # return

    ### Bin 파일 순차 처리, Hour.idx 를 JDAY 단위로 나누기
    for nBinIdx in range(0, nTotBinCnt) :
        jday = jday_arr[nBinIdx]

        with open(bin_file_arr[nBinIdx]) as binData :
            binDataLines = binData.read()

        binDataLines_tmp = binDataLines.split('\n')

        binDataArr = []      

        for i in range(0, len(binDataLines_tmp)) :            
            binDataArr_tmp = binDataLines_tmp[i].replace(' ', '').split('\t')

            if len(binDataArr_tmp[0]) <= 0 :
                continue

            binDataArr.append(binDataArr_tmp)

        nHourCnt = 0

        arr_Hour_Jday_Group = []

        ### 읽은 Bin 파일과 일치하는 hour.idx 의 데이터 갯수 추출
        for nHourIdx in range(0, len(timeArrayData)) :
            if timeArrayData[nHourIdx][0] != jday :
                continue

            arr_Hour_Jday_Group.append(timeArrayData[nHourIdx][1])
            nHourCnt += 1

        # bCalcFreqAvgYN

        # nDataCnt = 0
        # arr_Hour_Jday_Group = [ [0 for x in range(nHourCnt)] for y in range(1) ]
        # for nHourIdx in range(0, len(timeArrayData)) :
        #     if timeArrayData[nHourIdx][0] == jday :
        #         arr_Hour_Jday_Group[0][nDataCnt] = timeArrayData[nHourIdx]

        arr_Hour_Group = [ [0 for x in range(nHourCnt)] for y in range(grp_cnt) ]

        nSeq = 0
        group_val = [ 0 for x in range(grp_cnt) ]
        group_val_cnt = [ 0 for x in range(grp_cnt) ]

        for nHourIdx in range(0, len(timeArrayData)) :
            if timeArrayData[nHourIdx][0] != jday :
                continue

            for nBinDataIdx in range(0, len(binDataArr)) :
                if timeArrayData[nHourIdx][2] != binDataArr[nBinDataIdx][0] :
                    continue

                fFreq = 1 / float(binDataArr[nBinDataIdx][1])
                nDb = int(binDataArr[nBinDataIdx][2])

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

        # print(nCombineCnt, gs_figsize[nAxesCombineNum])
        # print(nBinIdx % gs_figsize[nAxesCombineNum])

        arrDayAvgVal_tmp = [ [0 for x in range(5)] for y in range(gs_figsize[nAxesCombineNum]) ]

        nDayHourCnt = 0
        nDatCnt = 0

        if nCombineCnt < gs_figsize[nAxesCombineNum] :            
            for nGrpNum in range(0, grp_cnt) :
                for nGrpDetailSeq in range(0, len(arr_Hour_Group[nGrpNum])) :
                    arr_Hour_Group_tmp[nGrpNum].append(arr_Hour_Group[nGrpNum][nGrpDetailSeq])
            
            for nJdayData in range(0, len(arr_Hour_Jday_Group)) :
                # arr_Hour_Jday_Group_tmp.append(arr_Hour_Jday_Group[nJdayData])
                arr_Hour_Jday_Group_tmp.append(nHourJdayGroupCount)

                if nTickTerm == 1 :
                    if nJdayData == 0 :
                        arrXTickPos.append(nHourJdayGroupCount)
                elif nTickTerm > 1 :
                    if nJdayData == 0 and nCombineCnt % (nTickTerm - 1) == 0 :
                        arrXTickPos.append(nHourJdayGroupCount)

                nHourJdayGroupCount += 1
                nDayHourCnt += 1

        if bCalcFreqAvgYN == True :
            for nGrpNum in range(0, grp_cnt) :
                # print(len(arrDayAvgVal_tmp), nGrpNum, nHourJdayGroupCount, nDayHourCnt)
                arrDayAvgVal_tmp[nCombineCnt][nGrpNum] = sum(arr_Hour_Group_tmp[nGrpNum][(nHourJdayGroupCount - nDayHourCnt):nHourJdayGroupCount]) / nDayHourCnt
            
            arrDayAvgVal[nCombineCnt] = arrDayAvgVal_tmp[nCombineCnt]

        nCombineCnt += 1
            
        if nCombineCnt < gs_figsize[nAxesCombineNum] :
            continue

        ### 데이터 Pivoting 일별 배열 -> 주파수대역별 배열
        if bCalcFreqAvgYN == True :
            for nDay in range(0, len(arrDayAvgVal)) :
                for nPvDay in range(0, len(arrDayAvgVal_pv)) :
                    arrDayAvgVal_pv[nPvDay][nDay] = arrDayAvgVal[nDay][nPvDay]

        nCombineCnt = 0
        nHourJdayGroupCount = 0

        axs[nAxesCombineNum].set_ylabel(r'Power [10log10(m**2/sec**4/Hz)] [dB]', fontsize=8)
        axs[nAxesCombineNum].yaxis.offsetText.set_fontsize(8)
        axs[nAxesCombineNum].yaxis.set_tick_params(labelsize=8)

        # if nTotBinCnt > 10 :
        #     if nAxesCombineNum == 0 :# or nBinIdx % 3 == 0 :
        #         if nRotation == 0 :
        #             axs[nAxesCombineNum].set_xlabel(year_arr[nAxesCombineNum] + "." + jday_arr[nAxesCombineNum], fontsize=8, horizontalalignment='right')
        #         else :
        #             axs[nAxesCombineNum].set_xlabel(jday_arr[nAxesCombineNum], fontsize=8, horizontalalignment='right', rotation=nRotation)

        # label_pos = axs[nAxesCombineNum].get_position()
        # print(label_pos)
        if bCalcFreqAvgYN == False :
            if (nBinIdx + 1) % nTickLabelTerm == 0 :
                nLastLabelIdx = (nBinIdx + 1) - nTickLabelTerm
                axs[nAxesCombineNum].set_xlabel(jday_arr[nLastLabelIdx], x=0, y=10, fontsize=8, horizontalalignment='left', rotation=nRotation)
            elif len(axs) - 1 == nAxesCombineNum :
                if bLastLabelSetYN == False :
                    bLastLabelSetYN = True
                    axs[nAxesCombineNum].set_xlabel(jday_arr[nLastLabelIdx + nTickLabelTerm], x=0, y=10, fontsize=8, horizontalalignment='left', rotation=nRotation)

        axs[nAxesCombineNum].grid('on', linestyle='--', axis='y', linewidth=0.5, alpha=0.7)
        # plt.grid(True, axis='y')

        for nBinAryIdx in range(0, grp_cnt) :
            bChkData = False

            for i in range(0, len(arr_Hour_Group_tmp[nBinAryIdx])) :
                # print(arr_Hour_Group_tmp[nBinAryIdx][i])
                if arr_Hour_Group_tmp[nBinAryIdx][i] != 0 :
                    bChkData = True
                    break
            
            if bChkData == False :
                continue    
            
            # fTotPower = sum(arr_Hour_Group_tmp[nBinAryIdx])
            # fPower = round(fTotPower / len(arr_Hour_Jday_Group_tmp), 2)
            # print(nAxesCombineNum, fPower)
            # print(arrDayNum, arrDayAvgVal_pv[nBinAryIdx])

            if nAxesCombineNum == 0 :
                if bCalcFreqAvgYN == True :
                    axs[nAxesCombineNum].plot(jday_arr_int, arrDayAvgVal_pv[nBinAryIdx], label=label[nBinAryIdx], linewidth=0.8)# alpha=0.3)
                else :
                    axs[nAxesCombineNum].plot(arr_Hour_Jday_Group_tmp, arr_Hour_Group_tmp[nBinAryIdx], label=label[nBinAryIdx], linewidth=0.8)# alpha=0.3)
                # print(len(arr_Hour_Jday_Group_tmp), len(arr_Hour_Group_tmp[nBinAryIdx]))
                # return
                # axs[nBinIdx].spines['left'].set_linewidth(1)
                # axs[nBinIdx].spines['left'].set_visible(False)
            else :
                if bCalcFreqAvgYN == True :
                    axs[nAxesCombineNum].plot(jday_arr_int, arrDayAvgVal_pv[nBinAryIdx], linewidth=0.8)# alpha=0.3)
                else :
                    axs[nAxesCombineNum].plot(arr_Hour_Jday_Group_tmp, arr_Hour_Group_tmp[nBinAryIdx], linewidth=0.8)#, label=nBinIdx)

                axs[nAxesCombineNum].spines['left'].set_linewidth(1)
                axs[nAxesCombineNum].spines['left'].set_visible(False)

        # print(arr_Hour_Group)
        # return

        ### GridSpec 사용에 따라, xlabel, xtick 강제로 표출 제외
        if nAxesCombineNum != 0 :
            plt.setp(axs[nAxesCombineNum].get_yticklabels(), visible=False)
            axs[nAxesCombineNum].tick_params(axis='y', which='both', length=0)        

        if bCalcFreqAvgYN == True :
            xlim = [jday_arr_int[0], jday_arr_int[len(jday_arr_int) - 1]]
        
            axs[nAxesCombineNum].set_xticks(ticks=jday_arr_int)
            # plt.setp(axs[nAxesCombineNum].get_xticklabels(), visible=False)
            axs[nAxesCombineNum].set_xlim(xlim)
            # print(jday_arr_int)
            # print(jday_arr_int[0], jday_arr_int[len(jday_arr_int) - 1])
        else :
            xlim = [arr_Hour_Jday_Group_tmp[0], arr_Hour_Jday_Group_tmp[len(arr_Hour_Jday_Group_tmp) - 1]]
            
            axs[nAxesCombineNum].set_xticks(ticks=arr_Hour_Jday_Group_tmp)
            plt.setp(axs[nAxesCombineNum].get_xticklabels(), visible=False)
            axs[nAxesCombineNum].set_xlim(xlim)
            # axs[nAxesCombineNum].minorticks_on()
            # plt.xlim(arr_Hour_Jday_Group_tmp[0], arr_Hour_Jday_Group_tmp[len(arr_Hour_Jday_Group_tmp) - 1])

        if len(arrXTickPos) <= 0 :
            axs[nAxesCombineNum].tick_params(axis='x', which='both', length=0)
        else :
            if bCalcFreqAvgYN == True :
                # axs[nAxesCombineNum].xaxis.set_major_locator(MultipleLocator(arrDayNum[len(arrDayNum) - 1]))

                arrMinorLocator = []
                arrMajorLocator = []

                # print(nGridTerm)

                if nTotBinCnt > 180 :
                    for nDayNum in range(0, len(jday_arr_int)) :
                        year_tmp = year_arr[nDayNum]
                        jday_tmp = jday_arr_int[nDayNum]
                        
                        if jday_tmp > 365 :
                            jday_tmp = jday_tmp - 365

                        ### JulianDay -> Normal DateTime
                        full_jday = [year_tmp, jday_tmp]
                        day = int(full_jday[1])
                        date = dt.datetime(int(full_jday[0]), 1, 1) + dt.timedelta(day - 1)

                        if date.day == 1 :
                            arrMajorLocator.append(jday_arr_int[nDayNum])
                        # if nDayNum == 0 or nDayNum % nGridTerm == 0 :
                        #     continue
                        else :
                            if date.isocalendar()[2] == 7 :
                                # print(date, jday_arr_int[nDayNum])
                                # print(mdates.weeks(date.day), jday_arr_int[nDayNum])
                                arrMinorLocator.append(jday_arr_int[nDayNum])
                elif nTotBinCnt > 30 :
                    for nDayNum in range(0, len(jday_arr_int)) :
                        if nDayNum == 0 or nDayNum % nGridTerm == 0 :
                            arrMajorLocator.append(jday_arr_int[nDayNum])
                        else :
                            if nDayNum % nMinorTickTerm == 0 :
                                arrMinorLocator.append(jday_arr_int[nDayNum])
                # print("MajorLocator : %s" %arrMajorLocator)
                # print("MinorLocator : %s" %arrMinorLocator)
                # return

                x_major_locator = FixedLocator(arrMajorLocator)
                axs[nAxesCombineNum].xaxis.set_major_locator(x_major_locator)
                # axs[nAxesCombineNum].xaxis.set_major_formatter(FormatStrFormatter('%d'))
                
                x_minor_locator = FixedLocator(arrMinorLocator)
                axs[nAxesCombineNum].xaxis.set_minor_locator(x_minor_locator)

                axs[nAxesCombineNum].xaxis.grid(True, which='major', ls='--', linewidth=0.5, alpha=0.7)# linestyle='--', axis='y', linewidth=0.5, alpha=0.7)

                # if nTotBinCnt < 60 :
                #     axs[nAxesCombineNum].xaxis.grid(True, which='minor', ls='--', linewidth=0.5, alpha=0.7)# linestyle='--', axis='y', linewidth=0.5, alpha=0.7)
                # print(jday_arr_int)

                # labels = [item.get_text() for item in axs[nAxesCombineNum].get_xticklabels()]
                labels = axs[nAxesCombineNum].get_xticks().tolist()

                if len(labels) > 0 :
                    year_major = 0
                    year_labelYN = False

                    for i in range(0, len(labels)) :
                        for j in range(0, len(jday_arr_int)) :
                            if labels[i] == jday_arr_int[j] :
                                year_tmp = year_arr[j]
                                jday_tmp = jday_arr_int[j]
                                
                                if jday_tmp > 365 :
                                    jday_tmp = jday_tmp - 365

                                if year_labelYN == False :
                                    year_major = year_tmp
                                else :
                                    if year_major != year_tmp :
                                        year_major = year_tmp
                                        year_labelYN = False

                                # print(jday_tmp, year_tmp)

                                # ### 표출 데이터의 마지막 날인 경우, 표출 제외
                                # if j == len(jday_arr_int) - 1 :
                                #     labels[i] = ""
                                #     continue

                                ### JulianDay -> Normal DateTime
                                full_jday = [year_tmp, jday_tmp]
                                day = int(full_jday[1])
                                date = dt.datetime(int(full_jday[0]), 1, 1) + dt.timedelta(day - 1)

                                if nTotBinCnt > 180 :
                                    if year_labelYN == False :
                                        date_str = date.strftime('%y.%m')
                                        year_labelYN = True
                                    else :
                                        date_str = date.strftime('%m')                                    
                                else :
                                    date_str = date.strftime('%m.%d')

                                labels[i] = date_str
                                # date_split = Split_Data(date.strftime('%Y/%m/%d'), "/")

                                # print(date_str)

                    axs[nAxesCombineNum].set_xticklabels(labels, rotation=nRotation, fontsize=8)
                # return

                for tick in axs[nAxesCombineNum].xaxis.get_major_ticks() :
                    tick.label.set_fontsize(8)
            else :
                axs[nAxesCombineNum].xaxis.set_major_locator(MultipleLocator(arr_Hour_Jday_Group_tmp[len(arr_Hour_Jday_Group_tmp) - 1]))
                # x_formatter = FixedFormatter(arrXTickPos)
                x_minor_locator = FixedLocator(arrXTickPos)
                # axs[nAxesCombineNum].xaxis.set_minor_formatter(x_formatter)
                axs[nAxesCombineNum].xaxis.set_minor_locator(x_minor_locator)
                # axs[nAxesCombineNum].tick_params(which='minor', color='r')#, visible=False)

        # print(arr_Hour_Jday_Group_tmp)
        # print(arrXTickPos)

        ### 데이터 병합용 배열 초기화
        arr_Hour_Group_tmp = [[] for y in range(grp_cnt)]
        arr_Hour_Jday_Group_tmp = []
        arrXTickPos = []
        nAxesCombineNum += 1

        if nAxesCombineNum < len(gs_figsize) :
            arrDayAvgVal = [ [0 for x in range(5)] for y in range(gs_figsize[nAxesCombineNum]) ]
            arrDayAvgVal_pv = [ [0 for x in range(gs_figsize[nAxesCombineNum])] for y in range(5) ]
            arrDayNum = [ x for x in range(gs_figsize[nAxesCombineNum])]

    for ax in axs :
        ax.label_outer()
        ax.set_ylim(-210, -50)
        ax.yaxis.set_major_locator(MultipleLocator(10)) # 10 단위로 tick표출

    plt.ylim(-210, -50)
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95], h_pad=0, w_pad=0)

    if nRotation == 0 :
        leg = fig.legend(loc='lower left', handlelength=0.3, labelspacing=0, columnspacing=1.5, bbox_to_anchor=(0.13,0.08, 0.5, 0.5), fontsize=8, ncol=5, framealpha=1.0)
    elif nRotation == 45 :
        axesPos = axs[0].get_position()
        axes_xsize = axesPos.x1 - axesPos.x0
        axes_xsize = round(axes_xsize, 2)
        # print(axes_xsize)        

        if axes_xsize <= 0.82 :
            leg = fig.legend(loc='lower left', handlelength=0.3, labelspacing=0, columnspacing=1.1, bbox_to_anchor=(0.13,0.11, 0.5, 0.5), fontsize=8, ncol=5, framealpha=1.0)
        elif axes_xsize <= 0.83 :
            leg = fig.legend(loc='lower left', handlelength=0.3, labelspacing=0, columnspacing=1.2, bbox_to_anchor=(0.13,0.11, 0.5, 0.5), fontsize=8, ncol=5, framealpha=1.0)
        elif axes_xsize <= 0.84 :
            leg = fig.legend(loc='lower left', handlelength=0.3, labelspacing=0, columnspacing=1.3, bbox_to_anchor=(0.13,0.11, 0.5, 0.5), fontsize=8, ncol=5, framealpha=1.0)
        else :
            leg = fig.legend(loc='lower left', handlelength=0.3, labelspacing=0, columnspacing=1.5, bbox_to_anchor=(0.13,0.11, 0.5, 0.5), fontsize=8, ncol=5, framealpha=1.0)

        # a = plt.legend()
        # bbox = a.get_window_extent()
        # print(bbox)
    else :
        leg = fig.legend(loc='lower left', handlelength=0.3, labelspacing=0, columnspacing=1.5, bbox_to_anchor=(0.13,0.09, 0.5, 0.5), fontsize=8, ncol=5, framealpha=1.0)
    
    for line in leg.get_lines() :
        line.set_linewidth(2.0)
    # fig.legend().get_lines().set_linewidth(1.0)

    ### subtitle 값 설정
    strTitleStartTime = ""
    strTitleEndTime = ""

    stDate = st_yearjday.split("/")
    day = int(stDate[1])
    date = dt.datetime(int(stDate[0]), 1, 1) + dt.timedelta(day - 1)
    date = date.strftime('%Y-%m-%d')
    strTitleStartTime = date

    edDate = ed_yearjday.split("/")
    day = int(edDate[1])
    date = dt.datetime(int(edDate[0]), 1, 1) + dt.timedelta(day - 1)
    date = date.strftime('%Y-%m-%d')
    strTitleEndTime = date

    strSubTitle = strTitleStartTime + " - " + strTitleEndTime + " (" + str(nTotBinCnt) + " days), " + str(nTotSegCnt) + " segments"
    plt.text(x_mid + 0.05, 0.92, strSubTitle, transform=plt.gcf().transFigure, ha='center')

    ### plot
    # plt.show()
    plt.savefig(output_file, bbox_inches='tight', pad_inches=0.2)
    plt.close()
    return 1

# def Proc_PSD(binfilepath, savepath, org, jday_split, net, sta, chn, loc, grouping_cnt, title, fig_size_x, fig_size_y) :
# def Proc_PSD() :
# def Proc_PSD(orgfilepath, savepath, org, year, jday_split, net, sta, chn, loc, interval_type, grp_cnt) :
# def Proc_PSD(analBinFileList, analIdxFileList, jday_idx_arr, savepath, net, sta, chn, loc, year, st_jday, ed_jday, intervaltype) :
def Proc_PSD(analBinFileList, analIdxFileList, year_idx_arr, jday_idx_arr, savepath, net, sta, chn, loc) :
    ### 저장 파일 경로 설정
    output_file_arr = Split_Data(savepath, '/')

    saveFileName = ""
    savePath = ""

    for output_file_arr_num in range(0, GetArraySize(output_file_arr)) :
        if output_file_arr_num == GetArraySize(output_file_arr) - 1 :
            saveFileName = output_file_arr[output_file_arr_num]
        else :
            savePath += output_file_arr[output_file_arr_num] + "/"
    ### 저장 경로 생성
    createDirectory(savePath)

    ### 타이틀, 파일명용 문자열 생성
    title = saveFileName.upper().replace(".PNG", "")
    
    saveFileName = savePath + "PSD_" + title + ".png"

    # print(savePath, saveFileName)

    # title = "Power Spectral Density (" + title + ")"
    title = net + " " + sta + " " + loc + " " + chn + "\n"

    ### 기존 파일 삭제
    removeFile(saveFileName)

    # freqList_Arr = []
    # freqGroupArrayList_Arr = []

    # xpix = 470 * fPixelPerInchVal * 2
    # ypix = 400 * fPixelPerInchVal * 2
    xpix = 607 * fPixelPerInchVal
    ypix = 531 * fPixelPerInchVal

    # plt.rc(usetex = True)
    fig = plt.figure(figsize=(xpix, ypix), dpi=nDpiVal)
    # fig = plt.figure(figsize=(8,5), dpi=100)
    ax = fig.add_subplot(1,1,1)

    ax.grid('on', linestyle='--', linewidth=0.5)#, alpha=1)
    ymax = -50 #max + 50# ((max - min) * 1.1)
    ymin = -200 #min - 50# ((max - min) * 1.1)

    plt.ylim(ymin, ymax)
    ax.set_ylim(ymin, ymax)#[min - 10, max + 10])
    yticks = np.arange(ymin, ymax + 1)

    ytick = []

    for ytick_cnt in range(0, len(yticks)) :
        if yticks[ytick_cnt] % 10 == 0 :
            ytick.append(yticks[ytick_cnt])

    plt.yticks(yticks)

    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks)
    yticks = ax.yaxis.get_major_ticks()

    for index, label in enumerate(ax.get_yaxis().get_ticklabels()) :
        if index % 10 != 0 :        
            yticks[index].set_visible(False)
        else :            
            yticks[index].set_visible(True)

    # ### 날짜별로 색상 변경
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

    # cname = []
    # for name, hex in matplotlib.colors.cnames.items() :
    #     cname.append(name)

    # print(len(cname))
    # sys.exit()

    # hsv = [0 / 360, 100 / 100, 100 / 100]
    h = 0
    s = 100
    v = 100
    r, g, b = matplotlib.colors.hsv_to_rgb([h / 360, s / 100, v / 100])
    cname = []

    for i in range(0, len(jday_idx_arr)) :
        if i == 0 :
            cname.append([r, g, b])
            # print(i, cname[0])
        else :
            h, s, v = matplotlib.colors.rgb_to_hsv([r, g, b])
            h = h * 360
            s = s * 100
            v = v * 100
            h = h + (360 / len(jday_idx_arr))

            if h >= 360 :
                h = h % 360
                if v >= 5 :
                    v -= 5
                else :
                    v = 100

            # print(h, s, v)
            r, g, b = matplotlib.colors.hsv_to_rgb([h / 360, s / 100, v / 100])
            # print(i, r, g, b)
            cname.append([r, g, b])

    cmap = plt.cm.get_cmap("rainbow")
    colors = cmap(np.linspace(0, 1, 7))
    
    # print(cname)
    # sys.exit()

    timeArrayCnt_tot = 0

    for nDataIdx in range(0, len(jday_idx_arr)) :
        ### 시간 데이터 처리
        openHourFileFullPath = analIdxFileList[nDataIdx]
        timeArrayData_tmp = []
        timeArrayData = []

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
        openAmpFileFullPath = analBinFileList[nDataIdx]
        freqReadData = []

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
            if( timeArrayData[i][0] == jday_idx_arr[nDataIdx] ) :
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

                    if float(freqReadData[j][1]) >= 100.0 :
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
                freqList.append(freqReadData[i][1])
            else :
                dataYN = False
                for j in range(0, len(freqList) ) :
                    if( freqReadData[i][1] == freqList[j] ) :
                        dataYN = True
                        break
                
                if float(freqReadData[i][1]) >= 100.0 :
                    continue

                if( dataYN == False ) :
                    freqList.append(freqReadData[i][1] )

        freqList = sorted(freqList)

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

        # nFreqVal = [ 0 for x in range(len(freqList)) ]
        nIdx = 1
        # nGroupFreqSeq = 0
        nCurrentGroupLen = 0

        for i in range(0, len(freqArrayList)) :
            for j in range(0, len(freqArrayList[i])) :
                freqGroupArrayList[j][i] = freqArrayList[i][j]

        # print(len(freqList))
        # print(len(freqGroupArrayList[0]))

        r = 0.0
        g = 0.0
        b = 255.00000
        # a = 1.0

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

        # print(nDataIdx)

        nClrIdx = 0

        # ### 월(7일 단위), 연(1개월) 단위로 색상 설정
        # if intervaltype == 'm' :
        #     # print(int((int(jday_idx_arr[nDataIdx]) - int(st_jday)) / 7))
        #     nClrIdx = int((int(jday_idx_arr[nDataIdx]) - int(st_jday)) / 7)
        # elif intervaltype == 'y' :
        #     for nMonth in range(1, 13) :
        #         nCurrentJulDay = juldate(int(year), nMonth, 1)

        #         if nMonth < 12 :
        #             nNextJulDay = juldate(int(year), nMonth + 1, 1)
        #         else :
        #             nNextJulDay = 365

        #         if int(jday_idx_arr[nDataIdx]) >= nCurrentJulDay and int(jday_idx_arr[nDataIdx]) <= nNextJulDay :
        #             nClrIdx = nMonth - 1
        #     # nClrIdx = int((int(jday_idx_arr[nDataIdx]) - int(st_jday)) / 12)
        
        # if nClrIdx >= len(colors) :
        #     nClrIdx = nClrIdx % len(colors)
        # ### 월(7일 단위), 연(1개월) 단위로 색상 설정 END

        ### 일 단위로 색상 설정
        if nDataIdx >= len(colors) :
            nClrIdx = nDataIdx % len(colors)
        else :
            nClrIdx = nDataIdx
        ### 일 단위로 색상 설정 END

        # print(nDataIdx, nClrIdx, intervaltype, colors[nClrIdx][0] * 255, colors[nClrIdx][1] * 255, colors[nClrIdx][2])

        strLabel = year_idx_arr[nDataIdx] + "." + jday_idx_arr[nDataIdx]

        for i in range(0, len(freqGroupArrayList)) :
            if i == 0 :
                ax.plot(freqList, freqGroupArrayList[i], label=strLabel, zorder=0, linewidth=1, alpha=0.3, color=colors[nClrIdx])#cname[nDataIdx])# color=(r, g / 255, b / 255))
            else :
                ax.plot(freqList, freqGroupArrayList[i], zorder=0, linewidth=1, alpha=0.3, color=colors[nClrIdx])#cname[nDataIdx])# color=(r, g / 255, b / 255))

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

        timeArrayCnt_tot += len(timeArrayCnt)

    st_year = year_idx_arr[0]
    st_jday = jday_idx_arr[0]
    ed_year = year_idx_arr[len(year_idx_arr) - 1]
    ed_jday = jday_idx_arr[len(jday_idx_arr) - 1]
    # title += str(len(timeArrayCnt)) + "PSDs : " + str(year) + ":" + str(st_jday) + " - " + str(year) + ":" + str(ed_jday) + "\n"
    title += str(timeArrayCnt_tot) + "PSDs : " + str(st_year) + ":" + str(st_jday) + " - " + str(ed_year) + ":" + str(ed_jday) + "\n"
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.xlim(freqList[0], freqList[len(freqList) - 1])
    # plt.xlim(str(int(float(xTickList[0]))), str(int(float(xTickList[len(xTickList) - 1]))))#xTickList[len(xTickList) - 1])
    # plt.yticks(fontsize=8)
    # plt.xticks(xTickList, fontsize=8)
    plt.title(str(title), fontsize=15)#, fontsize=8)
    plt.xlabel('Period (sec)')#, fontsize=8)
    plt.ylabel(r'Power [10log10(m**2/sec**4/Hz)] [dB]')#, fontsize=8)
    # plt.legend(title='Jday', loc='lower right', fontsize=8, ncol=2)

    # numitems = len(list(ax._get_legend_handles()))
    # print(numitems)

    # plt.xticks(rotation=60)
    # plt.subplots_adjust(top=0.825, bottom=0.145, left=0.125, right=0.837)
    plt.subplots_adjust(top=0.822, bottom=0.144, left=0.127, right=0.84)
    # print(saveFileName)
    # plt.savefig(str(saveFileName))
    # plt.colorbar(sc, label="")

    plt.show()
    plt.close()

def main():
    parser = argp.ArgumentParser()
    parser.add_argument('-ifp', '--inputfilepath', type=str, help="input file path")                # ex) /opt/eqm/src/qc/pdf_custom/log/test_y/KS.SEO2..HHZ/T
    parser.add_argument('-n', '--net', type=str, help="network code")                               # ex) KS
    parser.add_argument('-s', '--sta', type=str, help="station code")                               # ex) AMD
    parser.add_argument('-c', '--chn', type=str, help="channel code")                               # ex) HHZ
    parser.add_argument('-l', '--loc', type=str, default="--", help="location code")                # ex) --, 00
    parser.add_argument('-o', '--output', type=str, help="output image save full path")             # ex) /NFS/EQM/ANA/PSD/KS/2019/KS.SEO2.HHZ.2019.png
    parser.add_argument('-t', '--type', default="D", type=str, help="analysis type")                # ex) D or M or Y (일 단위, 월 단위, 연 단위) - 임시(20200116 미사용 상태)

    args = parser.parse_args()

    errMsg = CheckArguments(args)

    if len(errMsg) > 0 :
        print(errMsg)
        return -1

    basepath = args.inputfilepath
    net = str(args.net).upper()
    sta = str(args.sta).upper()
    chn = str(args.chn).upper()
    loc = args.loc
    savepath = args.output
    maketype = args.type

    if len(loc) <= 0 :
        loc = "--"

    if basepath == "" :
        return -1

    ### 상대 경로를 절대 경로로 변환하기 위해 현재 경로 저장
    sModulePath = os.getcwd()
    sModulePath = sModulePath.replace('\\\\', '/')
    sModulePath = sModulePath.replace('\\', '/')

    if len(basepath) < 2 :
        basepath = sModulePath + "/" + basepath
    else :
        if basepath[0] != '/' and ( basepath[1] != ':' and basepath[2] != '/' ) :
            basepath = sModulePath + "/" + basepath

    if len(savepath) < 2 :
        savepath = sModulePath + "/" + savepath
    else :
        if savepath[0] != '/' and ( savepath[1] != ':' and savepath[2] != '/' ) :
            savepath = sModulePath + "/" + savepath

    if not os.path.isdir(basepath) :
        return -1

    ### Hour.idx 파일 검색(basepath 하위에 하나만 존재)
    dir_lst = GetDirectoryList(basepath)

    if len(dir_lst) == 0 :
        print("Check inputfilepath argument!! inputfilepath = %s" % (basepath) )
        return -1

    # print(dir_lst)

    ### 디렉토리명 유효성 체크
    for idx in range(len(dir_lst) - 1, -1, -1) :
        if dir_lst[idx][0] != 'Y' :
            dir_lst.remove(dir_lst[idx])
            continue

        if len(dir_lst[idx]) != 5 :
            dir_lst.remove(dir_lst[idx])
            continue

        try:
            int(dir_lst[idx][1:])
        except Exception as err :
            print("not analysis directory. dir = %s (code=%s)" % (dir_lst[idx][1:], err))
            dir_lst.remove(dir_lst[idx])
            continue

    dir_lst.sort()

    hour_idx_fullpath_arr = []
    tmp_hour_idx_fullpath = ""

    for idx in range(0, len(dir_lst)) :
        chkPath = basepath + "/" + dir_lst[idx] + "/HOUR"
        tmp_hour_idx_fullpath = findFile(chkPath, "hour.idx")

        ### hour.idx 읽어서 데이터 붙이는 부분 개발 필요(2020.01.15)

        if len(tmp_hour_idx_fullpath) > 0 :
            hour_idx_fullpath_arr.append(tmp_hour_idx_fullpath)
            # break

    if len(hour_idx_fullpath_arr) <= 0 :
        print("Hour Idx File Not Found!!!")
        return -1

    hour_idx_fullpath_arr.sort()
    # print(hour_idx_fullpath_arr)
    # return

    ### 분석대상 bin 파일 검색(basepath 하위 년도/HOUR 하위의 모든 .bin 파일)
    bin_file_arr = []
    yearjday_arr = []
    st_yearjday = ""
    ed_yearjday = ""
    bFirst = False

    for idx in range(0, len(dir_lst)) :
        chkPath = basepath + "/" + dir_lst[idx] + "/HOUR"

        ret_lst = GetFileList(chkPath, ".bin")

        if len(ret_lst) > 0 :
            for i in range(0, len(ret_lst)) :
                tmp_bin_file_full_path = chkPath + "/" + ret_lst[i]
                bin_file_arr.append(tmp_bin_file_full_path)

                tmp_yearjday = dir_lst[idx][1:] + "/" + ret_lst[i][1:4]
                yearjday_arr.append(tmp_yearjday)

                # if bFirst == False :
                #     st_yearjday = dir_lst[idx][1:] + "/" + ret_lst[i][1:4]
                #     ed_yearjday = st_yearjday
                #     bFirst = True
                # else :
                #     ed_yearjday = dir_lst[idx][1:] + "/" + ret_lst[i][1:4]

            # print(chkPath, ",", ret_lst)

    if len(bin_file_arr) <= 0 :
        print("Bin File Not Found!!!")
        return -1

    if len(yearjday_arr) <= 0 :
        print("Year / Jday Data Not Found!!!")
        return -1

    yearjday_arr.sort()
    st_yearjday = yearjday_arr[0]
    ed_yearjday = yearjday_arr[len(yearjday_arr) - 1]
    
    if len(st_yearjday) <= 0 or len(ed_yearjday) <= 0 :
        print("Unknown Start JDAY or End JDAY")
        return -1

    # print("\nbefore")
    # print(bin_file_arr)

    ### Linux 상에서 자동 정렬이 안되는 문제로 강제 정렬
    bin_file_arr.sort()

    # print("\nafter")
    # print(bin_file_arr)
    # return

    # print(bin_file_arr)
    # print(st_yearjday, ed_yearjday)
    # return

    # Proc_PSD(analBinFileList, analIdxFileList, year_idx_arr, jday_idx_arr, savepath, net, sta, chn, loc)
    nRet = Proc_Spectrum(bin_file_arr, hour_idx_fullpath_arr, st_yearjday, ed_yearjday, savepath, net, sta, chn, loc, maketype)    
    return nRet

if __name__ == "__main__" :
    start_time = time.time()
    print(time.strftime("[%y%m%d] START %X", time.localtime()))
    nRet = main()

    if nRet == 1 :
        print("Make PST Success")
    else :
        print("Make PST Failed")

    end_time = time.time()
    print(time.strftime("[%y%m%d] END %X", time.localtime()))
    
    print("processing time : %s sec" %round(end_time - start_time, 4))