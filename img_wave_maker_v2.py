import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import argparse as argp
import obspy as op
import datetime as dt
import sys
import re
import time
import copy
# from dateutil import tz
# import pytz

fPixelPerInchVal = 0.026458333 * 0.393701
nDpiVal = 96

# 테스트용 스크립트
#python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_wave_maker_v2.py -i=D:/Project/EQM/DATA/KMA/2020/093/KS.JEJB.HHE.2020.093.00.00.00 -o=D:/Project/EQM/DATA/KMA/2020/WAV_KS.JEJB.HHN.2020.093.00.00.00.png -t=D
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

# def mergeDirectoryName(*parent_dir, *child_dir) :
#     retArr = []

#     for parent in parent_dir :
#         for child in child_dir :
#             retArr += parent + "/" + child

#     return retArr

def process(input_file, output_file, interval_type) :
    ### 상대 경로를 절대 경로로 변환
    sModulePath = os.getcwd()
    sModulePath = sModulePath.replace('\\\\', '/')
    sModulePath = sModulePath.replace('\\', '/')

    if input_file[0] != '/' and ( input_file[1] != ':' and input_file[2] != '/' ) :
        input_path_bin = sModulePath + "/" + input_path_bin
    
    if output_file[0] != '/' and ( output_file[1] != ':' and output_file[2] != '/' ) :
        output_file = sModulePath + "/" + output_file

    # if input_file[0] != '/' :
    #     input_file = sModulePath + "/" + input_file
    
    # if output_file[0] != '/' :
    #     output_file = sModulePath + "/" + output_file

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

    try :        
        st = op.read(input_file, format="MSEED")
    except Exception as err:
        print("Failed to read in file(%s) : code(%s)" % (input_file, err))
        return

    if len(st) > 1:
        st_tmp_merge = op.Stream()
        for j in range(0, len(st)):
            tr_tmp = op.Trace()
            tr_tmp = st[j]
            tr_tmp.stats.sampling_rate = round(tr_tmp.stats.sampling_rate)
            st_tmp_merge.append(tr_tmp)
        st_tmp_merge.merge(fill_value='interpolate')
        st = st_tmp_merge

    tr = st[0]
    tr.stats.sampling_rate = round(tr.stats.sampling_rate)

    ### 진폭 max, min 의 차이 계산
    tr_amplitude = tr.data.max() - tr.data.min()

    # ### 0점 보정
    tr.detrend()

    ### ymax = y축 top, ymin = y축 bottom
    ymax = tr.data.max() + (tr_amplitude * 0.1)
    ymin = tr.data.min() - (tr_amplitude * 0.1)

    ### 0점 위치가 가운데로 위치하게 하기 위하여, min, max 값을 큰 값으로 범위 동기화 . nkh 2020.04.06
    if abs(ymax) > abs(ymin) :
        ymin = abs(ymax) * -1
    elif abs(ymax) < abs(ymin) :
        ymax = abs(ymin)

    xPix = 1074 * fPixelPerInchVal
    yPix = 200 * fPixelPerInchVal

    fig = plt.figure(figsize=(xPix, yPix), dpi=nDpiVal)

    if interval_type == "D" :
        ### 일 단위 기존 파일 삭제
        removeFile(output_file)

        plt.clf()

        ax = fig.add_subplot(1, 1, 1)
        ax.grid('on', linestyle='--')

        # ### xlim 값 설정
        # startXlim = tr.times("matplotlib")[0] + 0.5000001
        # endXlim = tr.times("matplotlib")[0] + 1.5000001
        # ax.set_xlim(startXlim, endXlim)   

        plt.ylim(ymin, ymax)
        plt.xlabel('Time (KST)')
        plt.ylabel('Count')
        plt.grid(True)

        # print(str(tr.stats.starttime))
        # print(str(tr.stats.starttime + 86400 - 0.000001))
        strTitleStartTime = str(tr.stats.starttime + dt.timedelta(hours=9))
        strTitleEndTime = str(tr.stats.starttime + dt.timedelta(hours=9) + 86400 - 0.000001)

        ### 타이틀
        # plt.title(str(tr.stats.starttime) + " - " + str(tr.stats.endtime), fontdict={'fontsize':8})
        plt.title(strTitleStartTime + " - " + strTitleEndTime, fontdict={'fontsize':8})

        ### 그리기
        line = ax.plot(tr.times("matplotlib") + 0.375, tr.data)#, timezone='KST')

        ### ticklabel offset 미사용
        # ax.ticklabel_format(axis='y', useOffset=False, style='plain')

        ### 선두께 조절
        plt.setp(line, linewidth=0.3)

        ### x축의 표출 시간 포맷 설정
        # xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
        xformatter = mdates.DateFormatter('%H:%M:%S')#, tz=tz.gettz('KST/KDT'))

        ### x축의 표출 시간 간격 설정
        xlocator = mdates.HourLocator(byhour=[0,3,6,9,12,15,18,21], interval = 1)

        ax.xaxis.set_major_formatter(xformatter)
        ax.xaxis.set_major_locator(xlocator)

        ### 슈퍼 타이틀 설정
        strSupTitle = ""
        
        if len(tr.stats.location) > 0 :
            strSupTitle = tr.stats.network + "." + tr.stats.station + "." + tr.stats.channel + "_" + tr.stats.location
        else :
            strSupTitle = tr.stats.network + "." + tr.stats.station + "." + tr.stats.channel
        plt.suptitle(strSupTitle)

        # print(tr.times("matplotlib")[0], tr.times("matplotlib")[len(tr.data) - 1])
        # print(tr.times("matplotlib")[0] - 0.0000001, tr.times("matplotlib")[0] + 1.0000001)

        st = mdates.num2date(tr.times("matplotlib")[0] - 0.000001)#, tz=KST)
        ed = mdates.num2date(tr.times("matplotlib")[0] + 1.000001)#, tz=KST)

        st = st + dt.timedelta(hours=9)
        ed = ed + dt.timedelta(hours=9)
        # st.replace(tzinfo=)

        # print(st, tr.times("matplotlib")[0], mdates.date2num(st))

        startXlim = st# mdates.date2num(st)#tr.times("matplotlib")[0] + 0.000001
        endXlim = ed#mdates.date2num(ed)#endTime#tr.times("matplotlib")[0] + 1.000001

        ### 원본 데이터의 최종 시간이 강제 설정된 값보다 클 경우에 대한 처리(24시간 초과 데이터)
        # if tr.times("matplotlib")[len(tr.data) - 1] - endXlim > 0.000000 :
        #     print("true")
        #     endXlim = tr.times("matplotlib")[len(tr.data) - 1] + 0.0000001

        # plt.xlim(tr.times("matplotlib")[0] - 0.0000001, tr.times("matplotlib")[len(tr.data) - 1] + 0.0000001)
        # plt.xlim(tr.times("matplotlib")[0] - 0.0000001, tr.times("matplotlib")[0] + 1.0000001)
        plt.xlim(startXlim, endXlim)
        plt.yticks(fontsize=8)
        plt.xticks(fontsize=7, rotation=60)
        plt.subplots_adjust(bottom=0.36, right=0.96, top=0.80, left=0.075)
        plt.savefig(output_file)
        # plt.show()
    elif interval_type == "H" :
        # 0 ~ 359999, 360000 ~ 719999
        hour_samp_cnt = int(60 * 60 * st[0].stats.sampling_rate) - 1    # 1시간 샘플 수 (배열이 0부터 시작하므로 -1)
        semprateForSecond = float(1 / st[0].stats.sampling_rate)        # 샘플당 초 단위 환산

        # ### 시간 단위 저장 디렉토리명 설정
        # fullsavepath = savepath + "/" + org + "/" + net + "/" + sta + "/" + chn + "/" + date_split[0] + "/" + date_split[1] + "/" + date_split[2]# + "/" + orgfilename

        ### 시간 단위 저장 경로 확인(없으면 생성)
        createDirectory(savePath)

        saveFileName_Only = saveFileName.upper().replace(".PNG", "")

        for i in range(0, int(st[0].stats.npts / (hour_samp_cnt + 1))) :
            fullsavepath_hour = savePath

            plt.clf()

            xLimMin = 0.0
            xLimMax = 0.0

            ax = fig.add_subplot(1, 1, 1)
            ax.grid('on', linestyle='--')

            ### y축 고정
            plt.ylim(ymin, ymax)

            plt.xlabel('Time (KST)')
            plt.ylabel('Count')
            plt.grid(True)

            ### 시간 단위 저장 파일명 설정
            if i < 10 :
                fullsavepath_hour += saveFileName_Only + "_0" + str(i) + ".PNG"
            else :
                fullsavepath_hour += saveFileName_Only + "_" + str(i) + ".PNG"

            ### 시간 단위 기존 파일 삭제
            removeFile(fullsavepath_hour)

            line = ""

            if i == 0 :
                ### 타이틀
                plt.title(str(tr.stats.starttime + dt.timedelta(hours=9)) + " - " + str(tr.stats.starttime + dt.timedelta(hours=9) + (60 * 60 - semprateForSecond)), fontdict={'fontsize':8})

                ### 그리기
                line = ax.plot(tr.times("matplotlib")[i:i + hour_samp_cnt] + 0.375, tr.data[i:i + hour_samp_cnt])

                # xLimMin = tr.times("matplotlib")[i] - 0.0000001
                # xLimMax = tr.times("matplotlib")[i + hour_samp_cnt] + 0.0000001

                st = mdates.num2date(tr.times("matplotlib")[i] - 0.0000001)#, tz=KST)
                ed = mdates.num2date(tr.times("matplotlib")[i + hour_samp_cnt] + 0.0000001)#, tz=KST)

                xLimMin = st + dt.timedelta(hours=9)
                xLimMax = ed + dt.timedelta(hours=9)
            else :
                ### 타이틀
                plt.title(str(tr.stats.starttime + dt.timedelta(hours=9) + (i * (60 * 60))) + " - " + str(tr.stats.starttime + dt.timedelta(hours=9) + (((i + 1) * (60 * 60)) - semprateForSecond)), fontdict={'fontsize':8})

                ### 그리기
                line = ax.plot(tr.times("matplotlib")[(i * (hour_samp_cnt + 1)):((i * (hour_samp_cnt + 1)) + hour_samp_cnt)] + 0.375, tr.data[(i * (hour_samp_cnt + 1)):((i * (hour_samp_cnt + 1)) + hour_samp_cnt)])

                # xLimMin = tr.times("matplotlib")[(i * (hour_samp_cnt + 1))] - 0.0000001
                # xLimMax = tr.times("matplotlib")[((i * (hour_samp_cnt + 1)) + hour_samp_cnt)] + 0.0000001

                st = mdates.num2date(tr.times("matplotlib")[(i * (hour_samp_cnt + 1))] - 0.0000001)
                ed = mdates.num2date(tr.times("matplotlib")[((i * (hour_samp_cnt + 1)) + hour_samp_cnt)] + 0.0000001)

                xLimMin = st + dt.timedelta(hours=9)
                xLimMax = ed + dt.timedelta(hours=9)

            ### 선두께 조절
            plt.setp(line, linewidth=0.3)

            ax.xaxis_date()

            ### x축의 표출 시간 포맷 설정
            # xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
            xformatter = mdates.DateFormatter('%H:%M:%S')

            ### x축의 표출 시간 간격 설정
            xlocator = mdates.MinuteLocator(byminute=[0,15,30,45], interval = 1)

            ax.xaxis.set_major_formatter(xformatter)
            ax.xaxis.set_major_locator(xlocator)

            ### 슈퍼 타이틀 설정
            strSupTitle = ""
            
            if len(tr.stats.location) > 0 :
                strSupTitle = tr.stats.network + "." + tr.stats.station + "." + tr.stats.channel + "_" + tr.stats.location
            else :
                strSupTitle = tr.stats.network + "." + tr.stats.station + "." + tr.stats.channel
            plt.suptitle(strSupTitle)

            # print(xLimMin, xLimMax)
            
            plt.xlim(xLimMin, xLimMax)
            plt.yticks(fontsize=8)
            plt.xticks(fontsize=7, rotation=60)
            plt.subplots_adjust(bottom=0.36, right=0.96, top=0.80, left=0.075)
            plt.savefig(fullsavepath_hour)
            
            # plt.show()

    plt.close()

def main():
    parser = argp.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help="analysis file full path")                  # ex) /DATA/EQK/RAW1/KMA/2019/065/KS.SEO2.HHZ.2019.065.00.00.00
    parser.add_argument('-o', '--output', type=str, help="analysis result file full path")          # ex) /DATA/EQM/WAVE/KS/2019/065/KS.SEO2.HHZ.2019.065.00.00.00.png
    parser.add_argument('-t', '--type', type=str, default="D", help="save interval type")          # ex) 'D' or 'H' or 'D,H'

    args = parser.parse_args()

    errMsg = CheckArguments(args)

    if len(errMsg) > 0 :
        print(errMsg)
        return

    input_file = str(args.input).upper()
    output_file = args.output
    interval_type = str(args.type).upper()

    ### 복수일 수 있는 인자값을 배열로 저장
    interval_type_arr = Split_Data(interval_type, ",")

    for it_arr_num in range(0, GetArraySize(interval_type_arr)) :
        process(input_file, output_file, interval_type_arr[it_arr_num])

if __name__ == "__main__":
    start_time = time.time()
    print(time.strftime("[%y%m%d] START %X", time.localtime()))
    main()

    end_time = time.time()
    print(time.strftime("[%y%m%d] END %X", time.localtime()))
    
    print("processing time : %s sec" %round(end_time - start_time, 4))
