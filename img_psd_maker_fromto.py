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
import colorsys

fPixelPerInchVal = 0.026458333 * 0.393701
nDpiVal = 96
grp_cnt = 5

# 테스트용 스크립트
#python img_psd_maker_month_year.py -fp=D:/Project/EQM/DATA/temp/PSD -o=KS -n=KS -s=SEO2 -c=HHZ -l=-- -sd=20191101 -ed=20191130 -sp=D:/Project/EQM/DATA/temp/PSD/KS.SEO2.HHZ.2019.png
#python img_psd_maker_month_year.py -fp=./PSD -o=KS -n=KS -s=SEO2 -c=HHZ -l=-- -sd=20191101 -ed=20191130 -sp=./PSD/KS.SEO2.HHZ.2019.png
#python img_psd_maker_month_year.py -fp=./PSD -o=KS -n=KS -s=SEO2 -c=HHZ -l=-- -y=2019 -sj=274 -ej=275 -sp=./PSD/KS
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

# def Proc_Spectrum(binfilepath, savepath, org, jday_split, net, sta, chn, loc, grouping_cnt, title, fig_size_x, fig_size_y) :
# def Proc_Spectrum() :
# def Proc_Spectrum(orgfilepath, savepath, org, year, jday_split, net, sta, chn, loc, interval_type, grp_cnt) :
# def Proc_Spectrum(analBinFileList, analIdxFileList, jday_idx_arr, savepath, net, sta, chn, loc, year, st_jday, ed_jday, intervaltype) :
def Proc_Spectrum(analBinFileList, analIdxFileList, year_idx_arr, jday_idx_arr, savepath, net, sta, chn, loc) :
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
    saveFileName = savePath + "PST_" + saveFileName.upper().replace(".PNG", "") + ".png"

    title = net + " " + sta + " " + loc + " " + chn + "\n"

    ### 기존 파일 삭제
    removeFile(saveFileName)

    xPix = 537 * fPixelPerInchVal * 2
    yPix = 200 * fPixelPerInchVal * 2

    fig = plt.figure(figsize=(xPix, yPix), dpi=nDpiVal)
    ax = fig.add_subplot(1,1,1)

    ax.grid('on', linestyle='--', linewidth=0.5)#, alpha=1)
    ymax = -50
    ymin = -200

    plt.ylim(ymin, ymax)
    ax.set_ylim(ymin, ymax)
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

    cmap = plt.cm.get_cmap("rainbow")
    colors = cmap(np.linspace(0, 1, 7))

    timeArrayCnt_g = []
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

        ### 주파수 그룹화
        nIdx = 1
        #arrIntervalNum = []    
        nGroupCnt = int(grp_cnt)
        arrIntervalNum = [ [0 for x in range(2)] for y in range(nGroupCnt) ]
        arrAmpInterval = [ [0 for x in range(2)] for y in range(nGroupCnt) ]

        # 주요주파수 대역 하드코딩(2019.11.07)
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

        # print(arrIntervalNum)
        # print(arrAmpInterval)
        # print(freqList)
        # sys.exit()
        nMajor = 0
        nMinor = 0
        bChkMajor = False
        bChkMinor = False
        bChkDataYN = False
        bLoop = True

        while bLoop :
            for i in range(0, len(freqList)) :
                if nMajor >= nGroupCnt :
                    bLoop = False
                    break

                fFreq = round(float(freqList[i]), 6)
                fAmpInterval = round(float(arrAmpInterval[nMajor][nMinor]), 6)
                fAmpInterval_Max = 0

                if bChkMajor == False and bChkMinor == False :
                    fAmpInterval_Max = round(float(arrAmpInterval[nMajor][1]), 6)

                # print(i, len(freqList) - 1, bChkDataYN, bChkMajor, bChkMinor, fFreq, fAmpInterval, nMajor, nMinor)

                if bChkMajor == False :
                    if fFreq >= fAmpInterval :
                        if bChkMinor == False :
                            if fFreq >= fAmpInterval_Max :
                                if i == len(freqList) - 1 :
                                    arrIntervalNum[nMajor][0] = -1
                                    arrIntervalNum[nMajor][1] = -1
                                    nMajor += 1
                                    nMinor = 0
                                    bChkMajor = False
                                    bChkMinor = False                                
                                    break
                                else :
                                    continue

                        arrIntervalNum[nMajor][nMinor] = i
                        bChkMajor = True
                        bChkMinor = False
                        nMinor = 1
                        bChkDataYN = True
                elif bChkMinor == False :
                    if fFreq >= fAmpInterval :
                        arrIntervalNum[nMajor][nMinor] = i - 1
                        bChkMajor = False
                        bChkMinor = True
                        nMajor = nMajor + nMinor
                        nMinor = 0
                        bChkDataYN = True
                    else :
                        if i == len(freqList) - 1 :
                            if fFreq <= fAmpInterval :
                                arrIntervalNum[nMajor][nMinor] = i
                                bChkMajor = False
                                bChkMinor = True
                                nMajor = nMajor + nMinor
                                nMinor = 0
                                bChkDataYN = True

                if bChkDataYN == True :
                    bChkDataYN = False
                else :
                    if i == len(freqList) - 1 :
                        if bChkMajor == True and bChkMinor == False :
                            print("Don't Analysis Data. Process End!!!")
                            sys.exit()

                        i = 0
                        nMajor += 1
                        nMinor = 0
                        bChkMajor = False
                        bChkMinor = False

        # print(arrIntervalNum)
        # sys.exit()

        # for i in range(0, len(freqList)) :
        #     nIndex = int((float(len(freqList)) / nGroupCnt) * nIdx)
        #     print(i, nIdx, nIndex, freqList[i])

        #     if i == nIndex or i == len(freqList) - 1 :
        #         arrIntervalNum.append(i)
        #         nIdx += 1

        arrGroupFreq = []
        fFreqVal = 0.0
        nIdx = 1
        nIntervalSeq = 0
        nCurrentGroupLen = 0
        bLoop = True

        while bLoop :
            for i in range(0, len(freqList)) :
                if nIntervalSeq >= nGroupCnt :
                    bLoop = False
                    break

                # print(i, nIntervalSeq, arrIntervalNum[nIntervalSeq][0], arrIntervalNum[nIntervalSeq][1])

                if i > arrIntervalNum[nIntervalSeq][0] and i < arrIntervalNum[nIntervalSeq][1] :
                    fFreqVal += float(freqList[i])
                    nCurrentGroupLen += 1
                elif i == arrIntervalNum[nIntervalSeq][1] :
                    fFreqVal += float(freqList[i])
                    nCurrentGroupLen += 1
                    arrGroupFreq.append(round(fFreqVal / float(nCurrentGroupLen), 6))
                    fFreqVal = 0.0
                    nIntervalSeq += 1
                    nIdx += 1
                    nCurrentGroupLen = 0
                    break
                else :
                    if i == len(freqList) - 1 :
                        nIntervalSeq += 1

        # print(arrGroupFreq)
        # print(GetArraySize(arrGroupFreq))

        nGroupCnt = GetArraySize(arrGroupFreq)

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
        freqGroupArrayList = [ [0 for x in range(len(timeArrayCnt))] for y in range(len(arrGroupFreq)) ]

        ### 주파수 그룹별 dB값 그룹화
        for i in range(0, len(freqReadData) - 1) :
            for j in range(0, len(freqList)) :
                if freqReadData[i][1] == freqList[j] :
                    for k in range(0, len(timeArrayCnt)) :
                        if freqReadData[i][0] == timeArrayCnt[k] :
                            freqArrayList[j][k] = int(freqReadData[i][2])
                            break

        nFreqVal = [ 0 for x in range(len(timeArrayCnt)) ]
        nIdx = 1
        nGroupFreqSeq = 0
        nCurrentGroupLen = 0
        bLoop = True
        nGap = 0

        # print(arrIntervalNum)
        # sys.exit()

        while bLoop :
            for i in range(0, len(freqArrayList)) :
                if nGroupFreqSeq - nGap >= nGroupCnt :
                    bLoop = False
                    break

                if i < arrIntervalNum[nGroupFreqSeq][0] or i > arrIntervalNum[nGroupFreqSeq][1] :
                    if i == len(freqArrayList) - 1 :
                        if nCurrentGroupLen <= 0 :
                            nGap += 1

                        nCurrentGroupLen = 0
                        nGroupFreqSeq += 1
                        break
                    else :
                        continue

                for j in range(0, len(freqArrayList[i])) :
                    if nGroupFreqSeq - nGap >= len(arrIntervalNum) :
                        nGroupFreqSeq = 0

                    nFreqVal[j] += int(freqArrayList[i][j])

                # print(i, j)

                if i > arrIntervalNum[nGroupFreqSeq][0] and i < arrIntervalNum[nGroupFreqSeq][1] :
                # if i < arrIntervalNum[nGroupFreqSeq] :
                    nCurrentGroupLen += 1
                elif i == arrIntervalNum[nGroupFreqSeq][1] :
                    nCurrentGroupLen += 1

                    # print(nGroupFreqSeq - nGap, nCurrentGroupLen)

                    for k in range(0, len(nFreqVal)) :
                        freqGroupArrayList[nGroupFreqSeq - nGap][k] = nFreqVal[k] / nCurrentGroupLen
                        nFreqVal[k] = 0

                    nCurrentGroupLen = 0
                    nGroupFreqSeq += 1
                    break
                else :
                    if i == len(freqArrayList) - 1 :
                        if nCurrentGroupLen <= 0 :
                            nGap += 1

                        nCurrentGroupLen = 0
                        nGroupFreqSeq += 1

        # print(freqGroupArrayList)

        # print(len(freqArrayList[0]))
        # print(len(freqArrayList))

        nClrIdx = 0

        ### 일 단위로 색상 설정
        if nDataIdx >= len(colors) :
            nClrIdx = nDataIdx % len(colors)
        else :
            nClrIdx = nDataIdx
        ### 일 단위로 색상 설정 END

        ### X축(시간 데이터) 강제 동기화
        if len(timeArrayCnt_g) > 0 :
            for i in range(0, len(timeArrayCnt_g)) :
                if i >= len(timeArrayCnt) :
                    break
                timeArrayCnt[i] = timeArrayCnt_g[i]

        strLabel = year_idx_arr[nDataIdx] + "." + jday_idx_arr[nDataIdx]

        for i in range(0, len(freqGroupArrayList)) :
            if i == 0 :
                ax.plot(timeArrayCnt, freqGroupArrayList[i], label=strLabel, zorder=0, linewidth=1, alpha=1, color=colors[nClrIdx])
            else :
                ax.plot(timeArrayCnt, freqGroupArrayList[i], zorder=0, linewidth=0.8, alpha=1, color=colors[nClrIdx])

        # print(len(timeArrayCnt))

        xticks = ax.xaxis.get_major_ticks()

        nIdx = 1

        for index, label in enumerate(ax.get_xaxis().get_ticklabels()) :
            if index == 0 : # or index == len(timeArrayData) - 1 :
                xticks[index].set_visible(True)
                continue

            nSize = len(timeArrayCnt) - 1    

            # print(index, int((nSize / 4) * nIdx))
            if index == int((float(nSize) / 4) * nIdx) : #% 100 != 0 : 
                # print(index)
                xticks[index].set_visible(True)
                nIdx += 1
            else :
                xticks[index].set_visible(False)

        ### 시간 배열을 동일 시:분 으로 강제 동기화 하기 위해 설정
        if nDataIdx == 0 :
            for nTmArrNum in range(0, len(timeArrayCnt)) :
                timeArrayCnt_g.append(timeArrayCnt[nTmArrNum])
        else :
            if len(timeArrayCnt_g) < 47 :
                for nTmArrNum in range(0, len(timeArrayCnt)) :
                    if nTmArrNum < len(timeArrayCnt_g) :
                        continue
                    timeArrayCnt_g.append(timeArrayCnt[nTmArrNum])

        ### total PSD 누적
        timeArrayCnt_tot += len(timeArrayCnt)
                
    st_year = year_idx_arr[0]
    st_jday = jday_idx_arr[0]
    ed_year = year_idx_arr[len(year_idx_arr) - 1]
    ed_jday = jday_idx_arr[len(jday_idx_arr) - 1]
    # title += str(len(timeArrayCnt)) + "PSDs : " + str(year) + ":" + str(st_jday) + " - " + str(year) + ":" + str(ed_jday) + "\n"
    title += str(timeArrayCnt_tot) + "PSDs : " + str(st_year) + ":" + str(st_jday) + " - " + str(ed_year) + ":" + str(ed_jday) + "\n"
    plt.xticks(fontsize=8)#, rotation=45)
    plt.yticks(fontsize=8)
    plt.xlim(timeArrayCnt[0], timeArrayCnt[len(timeArrayCnt) - 1])
    plt.title(str(title), fontsize=15)# 'Spectrum (KS.SEO2.HHZ.2019.021.00.00.00)'
    plt.xlabel('Time (HH:mm)')
    # plt.ylabel('Power (dB)')
    plt.ylabel(r'Power [10log10(m**2/sec**4/Hz)] [dB]')#, fontsize=8)
    # plt.legend(title='Freq. Grp', loc='lower right', fontsize=8, ncol=2)

    plt.subplots_adjust(top=0.81, bottom=0.11, left=0.07, right=0.93)#, left=0.10, right=0.95)
    plt.savefig(str(saveFileName))

    # plt.show()
    plt.close()

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
    plt.savefig(str(saveFileName))
    # plt.colorbar(sc, label="")

    # plt.show()
    plt.close()

def main():    
    parser = argp.ArgumentParser()
    parser.add_argument('-fp', '--filepath', default="", type=str, help="analysis file path(HOUR Path)")                   # ex) /NFS/EQM/ANA/PSD
    parser.add_argument('-o', '--org', type=str, default="--", help="organization : Separate multiple names with comma")     # ex) KMA, KIGAM, KN, ETC
    parser.add_argument('-n', '--net', type=str, help="network code")        # ex) KS
    parser.add_argument('-s', '--sta', type=str, help="station code")        # ex) AMD
    parser.add_argument('-c', '--chn', type=str, help="channel code")        # ex) HHZ
    parser.add_argument('-l', '--loc', type=str, default="--", help="location code")       # ex) --, 00
    parser.add_argument('-sd', '--stday', type=str, help="process start date")   # ex) 2019.11.01 -> 20191101
    parser.add_argument('-ed', '--edday', type=str, help="process end date")    # ex) 2019.11.30 -> 20191130
    parser.add_argument('-sp', '--savepath', type=str, help="analysis response image save full path")        # ex) /NFS/EQM/ANA/PSD/KS/2019/KS.SEO2.HHZ.2019.png

    args = parser.parse_args()

    errMsg = CheckArguments(args)

    if len(errMsg) > 0 :
        print(errMsg)
        return

    basepath = args.filepath
    org = args.org    
    net = str(args.net).upper()
    sta = str(args.sta).upper()
    chn = str(args.chn).upper()
    loc = args.loc
    st_date = args.stday
    ed_date = args.edday
    savepath = args.savepath

    if len(loc) <= 0 :
        loc = "--"

    if basepath == "" :
        sys.exit()

    if not os.path.isdir(basepath) :
        return

    if st_date == "" or ed_date == "" :
        print("argument start date(stday) or end date(edday) not found!!!")
        return

    if len(st_date) != 8 or len(ed_date) != 8 :
        print("argument start date(stday) or end date(edday) length check!!!")
        return

    if int(st_date) > int(ed_date) :
        print("end date(edday) is less than start date(stday)!!!")
        return

    st_year = int(st_date[:4])
    ed_year = int(ed_date[:4])
    st_month = st_date[4:6]
    ed_month = ed_date[4:6]
    st_day = st_date[6:8]
    ed_day = ed_date[6:8]

    st_jday = ""
    ed_jday = ""

    bChkSameYear = False

    if st_year == ed_year :
        bChkSameYear = True

    st_jday = juldate(st_year, int(st_month), int(st_day))
    ed_jday = juldate(ed_year, int(ed_month), int(ed_day))

    if bChkSameYear == True and (int(ed_jday) < int(st_jday)) :
        print("ed_jday, st_jday Argument Data Error!!!")
        return

    # print(st_year, st_jday, ed_year, ed_jday)
    # sys.exit()

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

    year_idx_arr = []
    jday_idx_arr = []

    ### 시작 연도와 종료 연도가 같은 경우
    if bChkSameYear == True :
        nStJday = int(st_jday)
        nEdJday = int(ed_jday) + 1

        ### Jday 범위 산정
        for jday in range(nStJday, nEdJday) :
            strJday = ""
            if len(str(jday)) == 1 :
                strJday = "00" + str(jday)
            elif len(str(jday)) == 2 :
                strJday = "0" + str(jday)
            else :
                strJday = str(jday)

            jday_idx_arr.append(strJday)
            year_idx_arr.append(str(st_year))
    ### 시작 연도와 종료 연도가 다른 경우
    else :
        for i in range(st_year, ed_year + 1) :
            ### 시작 연도와 같은 경우
            if i == st_year :
                nStJday = int(st_jday)
                nEdJday = 365 + 1

                ### Jday 범위 산정
                for jday in range(nStJday, nEdJday) :
                    strJday = ""
                    if len(str(jday)) == 1 :
                        strJday = "00" + str(jday)
                    elif len(str(jday)) == 2 :
                        strJday = "0" + str(jday)
                    else :
                        strJday = str(jday)

                    jday_idx_arr.append(strJday)
                    year_idx_arr.append(str(i))
            ### 종료 연도와 같은 경우
            elif i == ed_year :
                nStJday = 1
                nEdJday = int(ed_jday) + 1

                ### Jday 범위 산정
                for jday in range(nStJday, nEdJday) :
                    strJday = ""
                    if len(str(jday)) == 1 :
                        strJday = "00" + str(jday)
                    elif len(str(jday)) == 2 :
                        strJday = "0" + str(jday)
                    else :
                        strJday = str(jday)

                    jday_idx_arr.append(strJday)
                    year_idx_arr.append(str(i))
            ### 시작 연도와 종료 연도 사이인 경우
            elif i > st_year and i < ed_year :
                nStJday = 1
                nEdJday = 365 + 1

                ### Jday 범위 산정
                for jday in range(nStJday, nEdJday) :
                    strJday = ""
                    if len(str(jday)) == 1 :
                        strJday = "00" + str(jday)
                    elif len(str(jday)) == 2 :
                        strJday = "0" + str(jday)
                    else :
                        strJday = str(jday)

                    jday_idx_arr.append(strJday)
                    year_idx_arr.append(str(i))

    # for i in range(0, len(jday_idx_arr)) :
    #     print(year_idx_arr[i], jday_idx_arr[i])
    # sys.exit()

    analBinFileList = []
    analIdxFileList = []
    orgBasePath = basepath
    basepath_jday_arr_all = []
    basepath_year_arr_all = []

    for nYear in range(st_year, ed_year + 1) :
        basepath = orgBasePath + "/" + org + "/" + str(nYear)
        basepath_arr = GetDirectoryList(basepath)

        if basepath_arr == "ERR" :
            # print("Check Failed GetDirectoryList(%s)" % (basepath))
            continue

        # print(nYear, basepath_arr)

        ### Jday 디렉토리 목록을 Start Jday <-> End Jday 범위에 있는 목록으로 갱신
        for i in range(len(basepath_arr) - 1, -1, -1) :
            nBasePathNum = int(basepath_arr[i])

            ### 시작 연도 데이터 처리
            if nYear == st_year :
                nStJday = int(st_jday)
                nEdJday = 365
            elif nYear == ed_year :
                nStJday = 1
                nEdJday = int(ed_jday)
            elif nYear > st_year and nYear < ed_year :
                nStJday = 1
                nEdJday = 365

            if nBasePathNum < nStJday :
                basepath_arr.remove(basepath_arr[i])
            elif nBasePathNum > nEdJday :
                basepath_arr.remove(basepath_arr[i])

        ### 포함되는 path 목록을 전체 목록에 추가
        for i in range(0, len(basepath_arr)) :
            basepath_jday_arr_all.append(basepath_arr[i])
            basepath_year_arr_all.append(str(nYear))

    # for i in range(0, len(basepath_jday_arr_all)) :
    #     print(basepath_year_arr_all[i], basepath_jday_arr_all[i])
    # sys.exit()

    if len(loc) <= 0 :
        loc = "--"

    year_idx_arr = []
    jday_idx_arr = []

    ### 분석 대상인 Bin, Idx 파일 찾아서 배열에 저장
    for i in range(0, len(basepath_jday_arr_all)) :
        year = basepath_year_arr_all[i]
        jday = basepath_jday_arr_all[i]
        # findPath = basepath + "/" + basepath_arr[i]
        findPath = orgBasePath + "/" + org + "/" + year + "/" + jday

        ### Bin 파일 검색
        if loc == "--" :
            findFileName = net + "." + sta + "." + chn + "." + year + "." + jday + ".00.00.00.hour.bin"
        else :
            findFileName = net + "." + sta + "." + chn + "_" + loc + "." + year + "." + jday + ".00.00.00.hour.bin"

        findBinFile = findFile(findPath, findFileName)

        ### Idx 파일 검색
        if loc == "--" :
            findFileName = net + "." + sta + "." + chn + "." + year + "." + jday + ".00.00.00.hour.idx"
        else :
            findFileName = net + "." + sta + "." + chn + "_" + loc + "." + year + "." + jday + ".00.00.00.hour.idx"

        findIdxFile = findFile(findPath, findFileName)

        ### Bin, Idx 파일이 모두 있는 경우만 배열에 저장
        if len(findBinFile) > 0 and len(findIdxFile) > 0 :
            year_idx_arr.append(year)
            jday_idx_arr.append(jday)
            analBinFileList.append(findBinFile)
            analIdxFileList.append(findIdxFile)

    # print(analBinFileList)
    # print(analIdxFileList)
    # print(year_idx_arr)
    # print(jday_idx_arr)
    # sys.exit()

    if len(jday_idx_arr) <= 0 or len(year_idx_arr) <= 0 :
        print("Anal Data Is Empty!!!")
        return

    Proc_PSD(analBinFileList, analIdxFileList, year_idx_arr, jday_idx_arr, savepath, net, sta, chn, loc)
    Proc_Spectrum(analBinFileList, analIdxFileList, year_idx_arr, jday_idx_arr, savepath, net, sta, chn, loc)

if __name__ == "__main__" :
    start_time = time.time()
    print(time.strftime("[%y%m%d] START %X", time.localtime()))
    main()

    end_time = time.time()
    print(time.strftime("[%y%m%d] END %X", time.localtime()))
    
    print("processing time : %s sec" %round(end_time - start_time, 4))