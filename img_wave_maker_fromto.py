import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import numpy as np
import argparse as argp
import obspy as op
import datetime as dt
import sys
import re
import time
import copy

fPixelPerInchVal = 0.026458333 * 0.393701
nDpiVal = 96

# 테스트용 스크립트
#python D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_wave_maker_fromto.py -ibp=D:/Project/EQM/DATA/KMA -iyj=2020/087,2020/088,2020/089,2020/090,2020/091,2020/092,2020/093 -o=D:/Project/EQM/DATA/KMA/2020/KS.JEJB.HHE.2020.087-093.png -n=KS -s=JEJB -c=HHE
#python D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_wave_maker_fromto.py -ibp=D:/Project/EQM/DATA/KMA -iyj=2019/020,2019/021,2019/022,2019/023,2019/024 -o=D:/Project/EQM/DATA/KMA/2019/test.png -n=KS -s=SEO2 -c=HHZ
#python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_wave_maker_v2.py -i=D:/Project/EQM/DATA/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00 -o=D:/Project/EQM/DATA/KMA/2019/020/WAV_KS.SEO2.HHZ.2019.020.00.00.00.png -t=D
#python img_amplitude_maker.py -fp=D:\Project\EQM\DATA -o=KMA -j=2019/020,2019/021 -n=KS -s=SEO2 -c=HHZ -sp=D:\Project\EQM\DATA -it=day
#python img_amplitude_maker.py --filepath_base=D:\Project\EQM\DATA --org=KMA --jday=2019/065 --net=* --sta=* --chn=* --savepath_base=D:\Project\EQM\DATA --interval_type=day

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

    for (path, dirname, files) in os.walk(root_path) :
        for f in files :
            findname = path + '/' + f
            if f == filename :
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

# def mergeDirectoryName(*parent_dir, *child_dir) :
#     retArr = []

#     for parent in parent_dir :
#         for child in child_dir :
#             retArr += parent + "/" + child

#     return retArr

def process(input_file_arr, output_file, year_jday_arr, nTotCnt) :
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

    ### MSEED 데이터 Stream 생성
    st = op.Stream()

    for i in range(0, nTotCnt) :
        # print(i, input_file_arr[i])
        try :
            # if i == 0 :
            #     st = op.read(input_file_arr[i], format="MSEED")
            # else :
            st_tmp = op.read(input_file_arr[i], format="MSEED")

            # print(len(st_tmp))

            if len(st_tmp) > 1 :
                st_tmp_merge = op.Stream()
                for j in range(0, len(st_tmp)) :
                    tr_tmp = op.Trace()
                    tr_tmp = st_tmp[j]
                    tr_tmp.stats.sampling_rate = round(tr_tmp.stats.sampling_rate)
                    st_tmp_merge.append(tr_tmp)
                st_tmp_merge.merge(fill_value='interpolate')
                st += st_tmp_merge
            else :
                st += st_tmp
        except Exception as err:
            print("Failed to read in file(%s) : code(%s)" % (input_file_arr[i], err))
            continue

    # print(nTotCnt, st)
    # sys.exit()

    xPix = 1074 * fPixelPerInchVal
    yPix = (111 + (89 * nTotCnt)) * fPixelPerInchVal

    # fig, axs = plt.subplots(nTotCnt, figsize=(xPix, yPix), dpi=nDpiVal, sharey=True, gridspec_kw={'hspace': 0, 'left':0.08, 'right':0.97, 'top':0.85, 'bottom':0.2})
    fig = plt.figure(1, figsize=(xPix, yPix), dpi=nDpiVal, constrained_layout=True)
    gs = gridspec.GridSpec(nTotCnt, 1)
    axs = [fig.add_subplot(ss) for ss in gs]

    # if nTotCnt == 1 :
    #     fig.subplots_adjust(top=0.80, bottom=0.2)
    # else :
    #     fig.subplots_adjust(bottom=0.2)

    x_mid = (fig.subplotpars.right + fig.subplotpars.left) / 2
    # y_mid = (fig.subplotpars.top + fig.subplotpars.bottom) / 2

    ### 기존 파일 삭제
    removeFile(output_file)

    strSupTitle = ""
    strTitleStartTime = ""
    strTitleEndTime = ""

    # nYmax = 0
    # nYmin = 0
    
    for i in range(0, nTotCnt) :
        year_jday = Split_Data(year_jday_arr[i], "/")

        tr = st[i]

        # print(i, tr.stats)

        ### 0점 보정
        tr.detrend()

        ### xlim 값 설정
        st_time = mdates.num2date(tr.times("matplotlib")[0] - 0.0000001)#, tz=KST)
        ed_time = mdates.num2date(tr.times("matplotlib")[0] + 1.0000001)#, tz=KST)

        st_time = st_time + dt.timedelta(hours=9)
        ed_time = ed_time + dt.timedelta(hours=9)

        startXlim = st_time #tr.times("matplotlib")[0] - 0.0000001
        endXlim = ed_time #tr.times("matplotlib")[0] + 1.0000001
        axs[i].set_xlim(startXlim, endXlim)

        ### 슈퍼 타이틀 설정
        if i == 0 :
            if len(tr.stats.location) > 0 :
                strSupTitle = tr.stats.network + "." + tr.stats.station + "." + tr.stats.channel + "_" + tr.stats.location
            else :
                strSupTitle = tr.stats.network + "." + tr.stats.station + "." + tr.stats.channel

        ### 서브 타이틀 표출을 위한 데이터의 시작, 종료 시간 설정 (메타데이터 기반 설정 방법)
        # if i == 0 :
        #     strTitleStartTime = str(tr.stats.starttime)

        #     if nTotCnt == 1 :
        #         strTitleEndTime = str(tr.stats.starttime + 86400 - 0.000001)

        # elif i + 1 == nTotCnt :
        #     strTitleEndTime = str(tr.stats.starttime + 86400 - 0.000001)

        ### 서브 타이틀 표출을 위한 데이터의 시작, 종료 시간 설정 (JDAY 기반 설정 방법)
        if i == 0 :
            ### JulianDay -> Normal DateTime
            day = int(year_jday[1])
            date = dt.datetime(int(year_jday[0]), 1, 1) + dt.timedelta(day - 1)
            date = date.strftime('%Y-%m-%d')
            strTitleStartTime = date + "(" + year_jday[1] + ")"
            strTitleEndTime = strTitleStartTime

        elif i + 1 == nTotCnt :
            ### JulianDay -> Normal DateTime
            day = int(year_jday[1])
            date = dt.datetime(int(year_jday[0]), 1, 1) + dt.timedelta(day - 1)
            date = date.strftime('%Y-%m-%d')

            strTitleEndTime = date + "(" + year_jday[1] + ")"

        # print(i, tr.stats.sampling_rate, tr.stats.delta, tr.stats.npts)
        tr.stats.sampling_rate = round(tr.stats.sampling_rate)
        # tr.stats.npts = 8640000        

        ### 진폭 max, min 의 차이 계산
        tr_amplitude = tr.data.max() - tr.data.min()

        ### ymax = y축 top, ymin = y축 bottom
        ymax = tr.data.max() + (tr_amplitude * 0.1)
        ymin = tr.data.min() - (tr_amplitude * 0.1)

        ### 0점 위치가 가운데로 위치하게 하기 위하여, min, max 값을 큰 값으로 범위 동기화 . nkh 2020.04.06
        if abs(ymax) > abs(ymin) :
            ymin = abs(ymax) * -1
        elif abs(ymax) < abs(ymin) :
            ymax = abs(ymin)

        # print(i, ymin, ymax)

        axs[i].grid('on', linestyle='--', axis='x')

        ### axs 의 Y 축을 전체 같게 설정하는 방식
        # plt.ylim(nYmin, nYmax)

        ### axs 의 Y 축을 각개로 설정하는  방식
        axs[i].set_ylim(ymin, ymax)#(nYmin, nYmax)
        # print(i, axs[i].get_ylim())

        # plt.xlabel('Time (UTC)')

        axs[i].set_ylabel(year_jday[1], fontsize=8)
        axs[i].yaxis.offsetText.set_fontsize(8)
        axs[i].yaxis.set_tick_params(labelsize=8)
        plt.grid(True, axis='x')

        # print(str(tr.stats.starttime))
        # print(str(tr.stats.starttime + 86400 - 0.000001))

        ### 그리기
        line = axs[i].plot(tr.times("matplotlib") + 0.375, tr.data)

        ### 선두께 조절
        plt.setp(line, linewidth=0.3)

        ### x축의 표출 시간 포맷 설정
        # xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
        xformatter = mdates.DateFormatter('%H:%M')

        ### x축의 표출 시간 간격 설정
        xlocator = mdates.HourLocator(byhour=[0,3,6,9,12,15,18,21], interval = 1)

        axs[i].xaxis.set_major_formatter(xformatter)
        axs[i].xaxis.set_major_locator(xlocator)
        # axs[0].set_xticklabels(visible=False)

        ### GridSpec 사용에 따라, xlabel, xtick 강제로 표출 제외
        if i + 1 != nTotCnt :
            plt.setp(axs[i].get_xticklabels(), visible=False)
            # plt.setp(axs[i].get_yticklabels(), visible=False)
            axs[i].tick_params(axis='x', which='both', length=0)
        
        plt.setp(axs[i].get_yticklabels(), visible=False)        
        axs[i].tick_params(axis='y', which='both', length=0)
        # axs[i].ticklabel_format(axis='y', useOffset=False, style='plain')

    for ax in axs :
        ax.ticklabel_format(axis='y', useOffset=False, style='plain')
        ax.label_outer()

    # plt.ticklabel_format(axis='y', useOffset=False)
        
        ### axs 의 Y 축을 전체 같게 설정하는 방식
        # ax.set_ylim(nYmin, nYmax)

    # ### x축 라벨 시간 표출 강제로 KST 로 변환 START
    # labels = axs[nTotCnt - 1].get_xticks().tolist()
    # print(labels)

    # if len(labels) > 0 :
    #     for i in range(0, len(labels)) :
    #         date_str = mdates.num2date(float(labels[i]) + 0.375)
    #         label_time = date_str.strftime('%H:%M')
    #         labels[i] = label_time
    #         # print(labels[i])
    
    # print(labels)
    # axs[nTotCnt - 1].set_xticklabels(labels, fontsize=8)
    # print(labels)
    # ### x축 라벨 시간 표출 강제로 KST 로 변환 END

    ### 타이틀
    # plt.title(str(tr.stats.starttime) + " - " + str(tr.stats.endtime), fontdict={'fontsize':8})
    axs[0].set_title(strSupTitle + " " + strTitleStartTime + " - " + strTitleEndTime, fontdict={'fontsize':8})

    # fig.get_axes()[0].annotate(strSupTitle, (0.5, 0.95), 
    #                         xycoords='figure fraction', x=x_mid
    #                         )
    # fig.suptitle(strSupTitle, x=x_mid)

    # print(tr.times("matplotlib")[0], tr.times("matplotlib")[len(tr.data) - 1])
    # print(tr.times("matplotlib")[0] - 0.0000001, tr.times("matplotlib")[0] + 1.0000001)

    ### 원본 데이터의 최종 시간이 강제 설정된 값보다 클 경우에 대한 처리(24시간 초과 데이터)
    # if tr.times("matplotlib")[len(tr.data) - 1] - endXlim > 0.000000 :
    #     print("true")
    #     endXlim = tr.times("matplotlib")[len(tr.data) - 1] + 0.0000001

    # plt.xlim(tr.times("matplotlib")[0] - 0.0000001, tr.times("matplotlib")[len(tr.data) - 1] + 0.0000001)
    # plt.xlim(tr.times("matplotlib")[0] - 0.0000001, tr.times("matplotlib")[0] + 1.0000001)
    # plt.xlim(startXlim, endXlim)
    # left, right = plt.xlim()
    # print(startXlim, endXlim)

    plt.yticks(fontsize=8)
    plt.xticks(fontsize=7)#, rotation=60)
    # plt.subplots_adjust(bottom=0.36, right=0.96, top=0.80, left=0.075)
    # plt.subplots_adjust(bottom=0.22, right=0.96, top=0.85, left=0.075, hspace=0)
    # plt.subplots_adjust(hspace=0)
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.95], h_pad=0)
    # plt.show()
    plt.savefig(output_file, bbox_inches='tight', pad_inches=0.2)

    plt.close()

def CheckAndMakeFileFullPathArr(inputbasepath, inputyearjday_arr, net, sta, chn, loc):
    nTotCnt = 0
    analFileFullPath_arr = []
    year_jday_arr = []

    for i in range(0, len(inputyearjday_arr)) :
        chkPath = inputbasepath + "/" + inputyearjday_arr[i]
        analFileName = net + "." + sta + "." + chn

        year_jday = inputyearjday_arr[i].replace("/", ".")

        analFileName += "." + year_jday

        if len(loc) > 0 :
            analFileName += "_" + loc

        analFileName += ".00.00.00"

        # print(chkPath, analFileName)

        ### mSEED 파일 존재 여부 확인
        analFileName = findFile(chkPath, analFileName)

        ### mSEED 파일 읽기 가능 여부 확인
        st = ""

        try :        
            st = op.read(analFileName, format="MSEED")
        except Exception as err:
            print("Failed to read in file(%s) : code(%s)" % (analFileName, err))
            continue

        if analFileName != "" :
            year_jday_arr.append(inputyearjday_arr[i])
            analFileFullPath_arr.append(analFileName)
            nTotCnt += 1

    return analFileFullPath_arr, year_jday_arr, nTotCnt

def main():
    parser = argp.ArgumentParser()
    parser.add_argument('-ibp', '--inputbasepath', type=str, help="analysis file base path")        # ex) /DATA/EQK/RAW1/KMA
    parser.add_argument('-iyj', '--inputyearjday', type=str, help="analysis file year / julian day")    # ex) 2019/065,2019/066
    parser.add_argument('-n', '--net', type=str, help="network code")   # ex) KS
    parser.add_argument('-s', '--sta', type=str, help="station code")   # ex) SEO2
    parser.add_argument('-c', '--chn', type=str, help="channel code")   # ex) HHZ
    parser.add_argument('-l', '--loc', default="--", type=str, help="location code")    # ex) 00
    parser.add_argument('-o', '--output', type=str, help="analysis result file full path")          # ex) /DATA/EQM/WAVE/KS/2019/065/KS.SEO2.HHZ.2019.065-2019.066.png

    args = parser.parse_args()

    errMsg = CheckArguments(args)

    if len(errMsg) > 0 :
        print(errMsg)
        return

    inputbasepath = args.inputbasepath
    inputyearjday = args.inputyearjday
    net = args.net
    sta = args.sta
    chn = args.chn
    loc = args.loc
    output_file = args.output

    if loc == "--" :
        loc = ""

    ### 복수일 수 있는 인자값을 배열로 저장
    inputyearjday_arr = Split_Data(inputyearjday, ",")

    ### 상대 경로를 절대 경로로 변환하기 위해 현재 경로 저장
    sModulePath = os.getcwd()
    sModulePath = sModulePath.replace('\\\\', '/')
    sModulePath = sModulePath.replace('\\', '/')

    if len(inputbasepath) < 2 :
        inputbasepath = sModulePath + "/" + inputbasepath
    else :
        if inputbasepath[0] != '/' and ( inputbasepath[1] != ':' and inputbasepath[2] != '/' ) :
            inputbasepath = sModulePath + "/" + inputbasepath

    if len(output_file) < 2 :
        output_file = sModulePath + "/" + output_file
    else :
        if output_file[0] != '/' and ( output_file[1] != ':' and output_file[2] != '/' ) :
            output_file = sModulePath + "/" + output_file

    ### 정상적으로 처리 가능한 mSEED 파일 갯수와 각각의 전체 경로 배열 생성
    analFileFullPath_arr, year_jday_arr, nTotCnt = CheckAndMakeFileFullPathArr(inputbasepath, inputyearjday_arr, net, sta, chn, loc)

    if nTotCnt > 0 :
        process(analFileFullPath_arr, output_file, year_jday_arr, nTotCnt)

if __name__ == "__main__":
    start_time = time.time()
    print(time.strftime("[%y%m%d] START %X", time.localtime()))
    main()

    end_time = time.time()
    print(time.strftime("[%y%m%d] END %X", time.localtime()))
    
    print("processing time : %s sec" %round(end_time - start_time, 4))