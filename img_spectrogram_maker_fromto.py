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
from obspy.io.xseed import Parser
from obspy.signal import PPSD
from obspy.core.inventory.inventory import read_inventory
from obspy.imaging.cm import pqlx
from obspy.imaging.cm import obspy_sequential
from obspy.imaging.util import _set_xaxis_obspy_dates

# 테스트용 스크립트
#python D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_spectrogram_maker_fromto.py -imbp=D:/Project/EQM/DATA/KMA -irbp=D:/Project/EQM/DATA/temp/RESP -irf=RESP.KS.SEO2..HHZ -o=D:/Project/EQM/DATA/KS.SEO2..HHZ.2019.png -n=KS -s=SEO2 -c=HHZ -l=-- -sd=20190120 -ed=20190128
#python img_spectrogram_maker_month_year.py -imbp=D:/Project/EQM/DATA/KMA -irbp=D:/Project/EQM/DATA/temp/RESP -irf=RESP.KS.SEO2..HHZ -o=D:/Project/EQM/DATA/KS.SEO2..HHZ.2019.png -n=KS -s=SEO2 -c=HHZ -l=-- -sd=20191001 -ed=20191130
#python img_spectrogram_maker_month_year.py -imbp=D:/Project/EQM/DATA/KMA/2019 -irbp=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/temp/RESP -irf=RESP.KS.SEO2..HHZ -o=D:/Project/EQM/TEST/Spectrogram/KS.SEO2..HHZ.2019.png -n=KS -s=SEO2 -c=HHZ -l=-- -sd=20190101 -ed=20191231
#python img_spectrogram_maker_month_year.py -imbp=D:/Project/EQM/DATA/KMA/2019 -irbp=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/temp/RESP -irf=RESP.KS.SEO2..HHZ -o=D:/Project/EQM/TEST/Spectrogram/KS.SEO2..HHZ.2019.png -y=2019 -n=KS -s=SEO2 -c=HHZ -l=-- -it=y
#python img_spectrogram_maker_month_year.py -imbp=D:/Project/EQM/DATA/KMA/2019 -irbp=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/temp/RESP -irf=RESP.KS.SEO2..HHZ -o=D:/Project/EQM/TEST/Spectrogram/KS.SEO2..HHZ.201910.png -y=2019 -m=10 -n=KS -s=SEO2 -c=HHZ -l=-- -it=m

fPixelPerInchVal = 0.026458333 * 0.393701
nDpiVal = 96

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

def juldate(year, month, day):
    jmonth = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    jday = jmonth[month - 1] + day

    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
        if month > 2:
            return jday + 1

    return jday

def plot_spectrogram_m(ppsd, cmap=obspy_sequential, clim=None, grid=True, filename=None, show=True):
    """
    Plot the temporal evolution of the PSD in a spectrogram-like plot.

    .. note::
        For example plots see the :ref:`Obspy Gallery <gallery>`.

    :type cmap: :class:`matplotlib.colors.Colormap`
    :param cmap: Specify a custom colormap instance. If not specified, then
        the default ObsPy sequential colormap is used.
    :type clim: list
    :param clim: Minimum/maximum dB values for lower/upper end of colormap.
        Specified as type ``float`` or ``None`` for no clipping on one end
        of the scale (e.g. ``clim=[-150, None]`` for a lower limit of
        ``-150`` dB and no clipping on upper end).
    :type grid: bool
    :param grid: Enable/disable grid in histogram plot.
    :type filename: str
    :param filename: Name of output file
    :type show: bool
    :param show: Enable/disable immediately showing the plot.
    """

    xPix = 537 * fPixelPerInchVal * 2
    yPix = 200 * fPixelPerInchVal * 2

    fig = plt.figure(figsize=(xPix, yPix), dpi=nDpiVal)
    ax = fig.add_subplot(1,1,1)#add_axes([0.1, 0.2, 0.85, 0.65])

    # fig, ax = plt.subplots()
    # fig.figure(figsize=(xPix, yPix), dpi=nDpiVal)

    quadmeshes = []
    yedges = ppsd.period_xedges

    for times, psds in ppsd._get_gapless_psd():
        xedges = [t.matplotlib_date for t in times] + [(times[-1] + ppsd.step).matplotlib_date]
        
        meshgrid_x, meshgrid_y = np.meshgrid(xedges, yedges)
        data = np.array(psds).T

        quadmesh = ax.pcolormesh(meshgrid_x, meshgrid_y, data, cmap=cmap, zorder=-1)
        quadmeshes.append(quadmesh)

    if clim is None:
        cmin = min(qm.get_clim()[0] for qm in quadmeshes)
        cmax = max(qm.get_clim()[1] for qm in quadmeshes)
        clim = (cmin, cmax)

    for quadmesh in quadmeshes:
        quadmesh.set_clim(*clim)

    cb = plt.colorbar(quadmesh, ax=ax)

    if grid:
        ax.grid()

    if ppsd.special_handling is None:
        cb.ax.set_ylabel('Amplitude [$m^2/s^4/Hz$] [dB]')
    else:
        cb.ax.set_ylabel('Amplitude [dB]')
    ax.set_ylabel('Period [s]')
    ax.set_xlabel('Time [UTC]')

    fig.autofmt_xdate()
    _set_xaxis_obspy_dates(ax)

    ax.set_yscale("log")
    ax.set_xlim(ppsd.times_processed[0].matplotlib_date,
                (ppsd.times_processed[-1] + ppsd.step).matplotlib_date)
    ax.set_ylim(yedges[0], yedges[-1])
    try:
        ax.set_facecolor('0.8')
    # mpl <2 has different API for setting Axes background color
    except AttributeError:
        ax.set_axis_bgcolor('0.8')

    fig.tight_layout()

    if filename is not None:
        plt.savefig(filename)
        plt.close()
    elif show:
        plt.draw()
        plt.show()
    else:
        plt.draw()
        return plt, fig, ax

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

def findFile(root_path, filename, ret_type) :
    if ret_type != "FULL" and ret_type != "FILE" :
        return "def findFile ret_type Error"

    retFileName = ""

    for (path, dirname, files) in os.walk(root_path) :
        for f in files :            
            if f == filename :
                if ret_type == "FULL" :
                    retFileName = path + "/" + f
                elif ret_type == "FILE" :
                    retFileName = f
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

# def process(orgfilepath, savepath, org, jday_split, orgfilename, net, sta, chn, loc, interval_type) :
# def process(orgfilepath, savepath, org, jday_split, orgfilename, net, sta, chn, loc, interval_type) :
# def process(analMseedFileList, analRespFileList, jday_idx_arr, output_file, year, net, sta, chn, loc) :
def process(analMseedFileList, analRespFileList, year_idx_arr_all, jday_idx_arr_all, output_file, net, sta, chn, loc, proc_range) :
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
    title = saveFileName.replace(".png", "")

    saveFileName = savePath + title + ".png"

    title = net + " " + sta + " " + loc + " " + chn + "\n"

    st_year = str(year_idx_arr_all[0])
    ed_year = str(year_idx_arr_all[len(year_idx_arr_all) - 1])

    title += st_year + ":" + jday_idx_arr_all[0] + " - " + ed_year + ":" + jday_idx_arr_all[len(jday_idx_arr_all) - 1]

    ### 기존 파일 삭제
    removeFile(saveFileName)

    bReadInv = False

    # print(jday_idx_arr_all[0], jday_idx_arr_all[len(jday_idx_arr_all) - 1])

    for nDataIdx in range(0, len(jday_idx_arr_all)) :
        ### MSEED 데이터 Stream 생성
        st = ""

        try :
            st = op.read(analMseedFileList[nDataIdx], format="MSEED")
        except Exception as err:
            print("Failed to read in file(%s) : code(%s)" % (analMseedFileList[nDataIdx], err))
            return
        tr = st[0]

        tr.stats.sampling_rate = round(tr.stats.sampling_rate)
        
        sampling_rate = tr.stats.sampling_rate
        if sampling_rate != 20.0 and sampling_rate != 100.0 and sampling_rate != 200.0 :            
            continue

        # print(jday_idx_arr[nDataIdx], tr.stats.npts)
        # if nDataIdx == 2 or nDataIdx == 3 :
        #     print(tr.stats)

        if bReadInv == False :
            ### RESP 데이터 기반 inventory load
            inv = read_inventory(analRespFileList[nDataIdx])
            # print(tr.stats)
            ppsd = PPSD(tr.stats, metadata=inv)
            # print(ppsd.id, ppsd.times_processed)
            bReadInv = True

        ppsd.add(st)

    # ppsd.plot(cmap=pqlx)
    # return

    if bReadInv == False :
        print("data Error!!!")
        return

    plot, fig, ax = plot_spectrogram_m(ppsd, cmap=pqlx, show=False, clim=[-200, -50])
    # fig = tr.spectrogram(show=False, log=True, per_lap=0.7, samp_rate=100, wlen=60, axes=ax, cmap=plt.get_cmap("jet"))#, cmap=pqlx)

    # semprateForSecond = float(1 / tr.stats.sampling_rate)

    # labels = [item.get_text() for item in ax.get_xticklabels()]
    # xticks = ax.xaxis.get_major_ticks()

    # for index, label in enumerate(ax.get_xaxis().get_ticklabels()) :
    #     if xticks[index].get_visible() == True :
    #         print(labels[index])
    #         labels[index] = str(tr.stats.starttime + (index * tr.stats.sampling_rate * 100))# + (index / tr.stats.sampling_rate))
            # print(labels[index])

    ### x축의 표출 포맷 / 시간 간격 설정
    xformatter = mdates.DateFormatter('%Y.%m.%d')#('%H:%M')

    # print(proc_range)
    if proc_range == 1 :
        xformatter = mdates.DateFormatter('%H:%M')
        xlocator = mdates.HourLocator(byhour=[0,3,6,9,12,15,18,21], interval = 1)
    elif proc_range <= 20 :
        xlocator = mdates.DayLocator(interval=1)
    elif proc_range <= 140 :
        xlocator = mdates.DayLocator(interval=7)
    else :
        xlocator = mdates.MonthLocator(interval=1)

    # xlocator = mdates.HourLocator(byhour=[0,3,6,9,12,15,18,21], interval = 1)

    ax.xaxis.set_major_formatter(xformatter)
    ax.xaxis.set_major_locator(xlocator)

    plot.xticks(fontsize=8, rotation=30)
    plot.yticks(fontsize=8)
    plot.xlabel('Time [UTC]')
    # plot.xlim(tr.times("matplotlib")[0] - 0.0000001, tr.times("matplotlib")[len(tr.data) - 1] + 0.0000001)
    # plot.title(str(tr.stats.starttime) + " - " + str(tr.stats.starttime + (60 * 60 - semprateForSecond)), fontdict={'fontsize':8})
    plot.title(str(title), fontsize=15)

    plot.subplots_adjust(top=0.85, bottom=0.17, left=0.1, right=1.0)
    plot.savefig(str(saveFileName))
    # plot.show()

    plot.close()

def main():
    parser = argp.ArgumentParser()
    parser.add_argument('-imbp', '--inputmseedbasepath', type=str, help="analysis mseed file base path")    # ex) /DATA/EQK/RAW1/KMA    
    parser.add_argument('-irbp', '--inputrespbasepath', type=str, help="use analysis RESP file base path")    # ex) /NFS/EQM/DAT/RESP
    parser.add_argument('-irf', '--inputrespfile', type=str, help="use analysis RESP file name")    # ex) RESP.KS.SEO2..HHZ
    parser.add_argument('-o', '--output', type=str, help="analysis result file full path")          # ex) /NFS/EQM/DAT/KS.SEO2.HHZ..201911.png
    parser.add_argument('-n', '--net', type=str, help="network code")   # ex) KS
    parser.add_argument('-s', '--sta', type=str, help="network code")   # ex) SEO2
    parser.add_argument('-c', '--chn', type=str, help="network code")   # ex) HHZ
    parser.add_argument('-l', '--loc', type=str, default="--", help="network code")   # ex) --
    parser.add_argument('-sd', '--stday', type=str, help="analysis start date")   # ex) 2019.11.01 -> 20191101
    parser.add_argument('-ed', '--edday', type=str, help="analysis end date") # ex) 2019.11.30 -> 20191130    

    args = parser.parse_args()

    errMsg = CheckArguments(args)

    if len(errMsg) > 0 :
        print(errMsg)
        return

    input_mseed_base_path = args.inputmseedbasepath
    output_file = args.output
    input_resp_base_path = args.inputrespbasepath
    input_resp_file_name = args.inputrespfile
    net = str(args.net).upper()
    sta = str(args.sta).upper()
    chn = str(args.chn).upper()
    loc = args.loc
    st_date = args.stday
    ed_date = args.edday

    if len(loc) <= 0 :
        loc = "--"

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

    # print(bChkSameYear, st_jday, ed_jday)
    # sys.exit()

    ### 상대 경로를 절대 경로로 변환
    sModulePath = os.getcwd()
    sModulePath = sModulePath.replace('\\\\', '/')
    sModulePath = sModulePath.replace('\\', '/')

    if len(input_mseed_base_path) < 2 :
        basepath = sModulePath + "/" + basepath
    else :
        if input_mseed_base_path[0] != '/' and ( input_mseed_base_path[1] != ':' and input_mseed_base_path[2] != '/' )  :
            input_mseed_base_path = sModulePath + "/" + input_mseed_base_path
    
    if len(output_file) < 2 :
        output_file = sModulePath + "/" + output_file
    else :
        if output_file[0] != '/' and ( output_file[1] != ':' and output_file[2] != '/' ) :
            output_file = sModulePath + "/" + output_file

    if len(input_resp_base_path) < 2 :
        input_resp_base_path = sModulePath + "/" + input_resp_base_path
    else :
        if input_resp_base_path[0] != '/' and ( input_resp_base_path[1] != ':' and input_resp_base_path[2] != '/' ) :
            input_resp_base_path = sModulePath + "/" + input_resp_base_path

    year_idx_arr_all = []
    mseedpath_arr_all = []
    proc_range = 0

    ### 시작 연도와 종료 연도가 같은 경우
    if bChkSameYear == True :
        strInputMseedPath = input_mseed_base_path + "/" + str(st_year)
        mseedpath_arr = GetDirectoryList(strInputMseedPath)

        if mseedpath_arr == "ERR" :
            print("Failed find Directory (%s)" % strInputMseedPath)
            return
        else :
            ### mSEED 대상 디렉토리 목록을 Start Jday <-> End Jday 범위에 있는 목록으로 갱신
            for i in range(len(mseedpath_arr) - 1, -1, -1) :
                nBasePathNum = int(mseedpath_arr[i])

                if nBasePathNum < st_jday :
                    mseedpath_arr.remove(mseedpath_arr[i])
                elif nBasePathNum > ed_jday :
                    mseedpath_arr.remove(mseedpath_arr[i])

            for i in range(0, len(mseedpath_arr)) :
                mseedpath_arr_all.append(mseedpath_arr[i])
                year_idx_arr_all.append(str(st_year))

        proc_range = ed_jday - st_jday + 1
    else :
        for nYear in range(st_year, ed_year + 1) :
            year = str(nYear)
            strInputMseedPath = input_mseed_base_path + "/" + year
            mseedpath_arr = GetDirectoryList(strInputMseedPath)

            if mseedpath_arr == "ERR" :
                print("Failed find Directory (%s)" % strInputMseedPath)
                continue
            else :
                nStJday = 0
                nEdJday = 0

                if nYear == st_year :
                    nStJday = st_jday
                    nEdJday = 365
                elif nYear == ed_year :
                    nStJday = 1
                    nEdJday = ed_jday
                elif nYear > st_year and nYear < ed_year :
                    nStJday = 1
                    nEdJday = 365

                ### mSEED 대상 디렉토리 목록을 Start Jday <-> End Jday 범위에 있는 목록으로 갱신
                for i in range(len(mseedpath_arr) - 1, -1, -1) :
                    nBasePathNum = int(mseedpath_arr[i])

                    if nBasePathNum < nStJday :
                        mseedpath_arr.remove(mseedpath_arr[i])
                    elif nBasePathNum > nEdJday :
                        mseedpath_arr.remove(mseedpath_arr[i])

                for i in range(0, len(mseedpath_arr)) :
                    mseedpath_arr_all.append(mseedpath_arr[i])
                    year_idx_arr_all.append(year)

                proc_range += nEdJday - nStJday + 1

    # print(proc_range)
    # sys.exit()
    # for i in range(0, len(mseedpath_arr_all)) :
    #     print(year_idx_arr_all[i], mseedpath_arr_all[i])

    # sys.exit()

    analMseedFileList = []
    analRespFileList = []

    jday_idx_arr = []
    jday_idx_arr = mseedpath_arr_all
    year_arr = year_idx_arr_all

    orgmseedbasepath = input_mseed_base_path

    jday_idx_arr_all = []
    year_idx_arr_all = []

    ### 분석 대상인 mSEED 파일 찾아서 배열에 저장
    for i in range(0, len(jday_idx_arr)) :
        year = year_arr[i]
        jday = jday_idx_arr[i]
        findPath = orgmseedbasepath + "/" + year + "/" + jday

        ### mSEED 파일 검색
        if loc == "--" :
            findFileName = net + "." + sta + "." + chn + "." + year + "." + jday + ".00.00.00"
        else :
            findFileName = net + "." + sta + "." + chn + "_" + loc + "." + year + "." + jday + ".00.00.00"

        findMseedFile = findFile(findPath, findFileName, "FULL")

        ### mSEED 파일이 있는 경우만 배열에 저장
        if len(findMseedFile) > 0 :
            jday_idx_arr_all.append(jday_idx_arr[i])
            year_idx_arr_all.append(year_arr[i])
            analMseedFileList.append(findMseedFile)

    ### 분석 대상인 mSEED 파일의 날짜와 매칭되는 RESP 파일이 없으면 Process 처리용 배열에서 삭제
    for i in range(len(jday_idx_arr_all) - 1, -1, -1) :
        year = str(year_idx_arr_all[i])
        
        day = int(jday_idx_arr_all[i])
        date = dt.datetime(int(year), 1, 1) + dt.timedelta(day - 1)
        date = date.strftime('%Y%m%d')
        
        ### M 먼저 탐색
        findPath = input_resp_base_path + "/M/" + year + "/" + date

        findRespFile = findFile(findPath, input_resp_file_name, "FULL")

        if len(findRespFile) > 0 :
            continue

        ### M 에 자료가 없으면 A 에서 탐색
        findPath = input_resp_base_path + "/A/" + year + "/" + date

        findRespFile = findFile(findPath, input_resp_file_name, "FULL")

        if len(findRespFile) > 0 :
            continue

        ### A 에 자료가 없으면 LAST 에서 탐색
        findPath = input_resp_base_path + "/LAST"

        findRespFile = findFile(findPath, input_resp_file_name, "FULL")

        if len(findRespFile) > 0 :
            continue

        jday_idx_arr_all.remove(jday_idx_arr[i])
        year_idx_arr_all.remove(year_arr[i])
        analMseedFileList.remove(analMseedFileList[i])

    ### 분석 대상인 mSEED 파일의 날짜와 매칭되는 RESP 파일 찾아서 배열에 저장
    for i in range(0, len(jday_idx_arr_all)) :
        year = str(year_idx_arr_all[i])

        day = int(jday_idx_arr_all[i])
        date = dt.datetime(int(year), 1, 1) + dt.timedelta(day - 1)
        date = date.strftime('%Y%m%d')
        
        ### M 먼저 탐색
        findPath = input_resp_base_path + "/M/" + year + "/" + date

        findRespFile = findFile(findPath, input_resp_file_name, "FULL")

        if len(findRespFile) > 0 :
            analRespFileList.append(findRespFile)
            continue

        ### M 에 자료가 없으면 A 에서 탐색
        findPath = input_resp_base_path + "/A/" + year + "/" + date

        findRespFile = findFile(findPath, input_resp_file_name, "FULL")

        if len(findRespFile) > 0 :
            analRespFileList.append(findRespFile)
            continue

        ### A 에 자료가 없으면 LAST 에서 탐색
        findPath = input_resp_base_path + "/LAST"

        findRespFile = findFile(findPath, input_resp_file_name, "FULL")

        if len(findRespFile) > 0 :
            analRespFileList.append(findRespFile)
            continue

    # print(len(year_idx_arr_all), len(jday_idx_arr_all), len(analMseedFileList), len(analRespFileList))
    # for i in range(0, len(jday_idx_arr_all)) :
    #     print(year_idx_arr_all[i], jday_idx_arr_all[i], analMseedFileList[i], analRespFileList[i])

    # sys.exit()

    if len(year_idx_arr_all) > 0 :
        process(analMseedFileList, analRespFileList, year_idx_arr_all, jday_idx_arr_all, output_file, net, sta, chn, loc, proc_range)

if __name__ == "__main__":
    start_time = time.time()
    print(time.strftime("[%y%m%d] START %X", time.localtime()))
    main()

    end_time = time.time()
    print(time.strftime("[%y%m%d] END %X", time.localtime()))
    
    print("processing time : %s sec" %round(end_time - start_time, 4))
