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
#python d:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/img_spectrogram_maker_v3.py -i=D:/Project/EQM/DATA/KMA/2019/021/KS.SEO2.HHZ.2019.021.00.00.00 -o=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/temp/KS.SEO2.HHZ.2019.021.00.00.00_v3.png -irbp=D:/Project/EQM/DATA/temp/RESP -irf=RESP.KS.SEO2..HHZ -y=2019 -j=021 -n=KS -s=SEO2 -c=HHZ
#python img_spectrogram_maker_v3.py -i=D:/Project/EQM/DATA/KMA/2019/020/KS.SEO2.HHZ.2019.020.00.00.00 -o=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/temp/KS.SEO2.HHZ.2019.020.00.00.00_v3.png -irbp=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/temp/RESP -irf=RESP.KS.SEO2..HHZ -y=2019 -j=020
#python img_spectrogram_maker_v3.py -i=D:/Project/EQM/DATA/KMA/2019/065/KS.YOJB.HHZ.2019.065.00.00.00 -o=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/temp/KS.YOJB.HHZ.2019.065.00.00.00.png -irbp=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/temp/RESP -irf=RESP.KS.YOJB..HHZ -y=2019 -j=065
#python img_spectrogram_maker_v3.py -i=D:/Project/EQM/DATA/KMA/2019/336/KS.SEO2.HHZ.2019.336.00.00.00 -o=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/temp/KS.SEO2.HHZ.2019.336.00.00.00.png -irbp=D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/temp/RESP -irf=RESP.KS.SEO2..HHZ -y=2019 -j=336

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
            if f == filename :
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
def process(input_file, output_file, input_resp_base_path, input_resp_file_name, year, jday, net, sta, chn, loc) :
    ### JulianDay -> Normal DateTime
    day = int(jday)
    date = dt.datetime(int(year), 1, 1) + dt.timedelta(day - 1)
    # date_split = Split_Data(date.strftime('%Y/%m/%d'), "/")
    date = date.strftime('%Y%m%d')

    # print(date)

    ### 상대 경로를 절대 경로로 변환
    sModulePath = os.getcwd()
    sModulePath = sModulePath.replace('\\\\', '/')
    sModulePath = sModulePath.replace('\\', '/')

    if input_file[0] != '/' and ( input_file[1] != ':' and input_file[2] != '/' )  :
        input_file = sModulePath + "/" + input_file
    
    if output_file[0] != '/' and ( output_file[1] != ':' and output_file[2] != '/' ) :
        output_file = sModulePath + "/" + output_file

    if input_resp_base_path[0] != '/' and ( input_resp_base_path[1] != ':' and input_resp_base_path[2] != '/' ) :
        input_resp_base_path = sModulePath + "/" + input_resp_base_path

    ### RESP 파일 탐색(M -> A -> LAST 순서로 탐색)
    ### M 경로에서 RESP 파일 탐색
    findPath = input_resp_base_path + "/M/" + year + "/" + date
    resp_file_name = findFile(findPath, input_resp_file_name)

    ### M 경로에 RESP 파일이 없으면 A 경로에서 탐색
    if resp_file_name == "" :
        findPath = input_resp_base_path + "/A/" + year + "/" + date
        resp_file_name = findFile(findPath, input_resp_file_name)

    ### A 경로에 RESP 파일이 없으면 LAST 경로에서 탐색
    if resp_file_name == "" :
        findPath = input_resp_base_path + "/LAST/"
        resp_file_name = findFile(findPath, input_resp_file_name)

        print(findPath, input_resp_file_name)

    if resp_file_name == "" :
        print("RESP file not found!!! process end")
        sys.exit()

    resp_file_fullpath = findPath + "/" + resp_file_name
    print("resp_file_fullpath", resp_file_fullpath)

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

    title = net + " " + sta + " " + loc + " " + chn + "\n(" + year + ":" + jday + ")\n"

    ### 기존 파일 삭제
    removeFile(saveFileName)

    ### MSEED 데이터 Stream 생성
    st = ""

    try :
        st = op.read(input_file, format="MSEED")
    except Exception as err:
        print("Failed to read in file(%s) : code(%s)" % (input_file, err))
        return
    tr = st[0]

    tr.stats.sampling_rate = round(tr.stats.sampling_rate)

    # print(tr.stats)

    ### RESP 데이터 기반 inventory load
    inv = read_inventory(resp_file_fullpath)
    # print(inv)

    ppsd = PPSD(tr.stats, metadata=inv)
    # print(ppsd.id, ppsd.times_processed)

    ppsd.add(st)

    # ppsd.plot(cmap=pqlx)
    # sys.exit()

    plot, fig, ax = plot_spectrogram_m(ppsd, cmap=pqlx, show=False, clim=[-200, -50])

    ### x축 시간 KST 변경을 위한  테스트 2020.03.11
    # left, right = plot.xlim()
    # st = mdates.num2date(tr.times("matplotlib")[0] - 0.000001)
    # ed = mdates.num2date(tr.times("matplotlib")[0] + 1.0)#00001)
    # st = st + dt.timedelta(hours=9)
    # ed = ed + dt.timedelta(hours=9)
    # delta = dt.timedelta(hours=1)
    # dates = mdates.drange(st, ed, delta)
    # print(dates)
    # s = np.random.rand(len(dates))

    # plot.plot_date(dates, s)
    # print(left, right)
    # plot.xlim(st, right)

    ### x축의 표출 포맷 / 시간 간격 설정
    xformatter = mdates.DateFormatter('%H:%M')
    xlocator = mdates.HourLocator(byhour=[0,3,6,9,12,15,18,21], interval = 1)

    ax.xaxis.set_major_formatter(xformatter)
    ax.xaxis.set_major_locator(xlocator)

    ### x축 라벨 시간 표출 강제로 KST 로 변환 START
    labels = ax.get_xticks().tolist()
    # print(labels)

    if len(labels) > 0 :
        for i in range(0, len(labels)) :
            date_str = mdates.num2date(float(labels[i]) + 0.375)
            label_time = date_str.strftime('%H:%M')
            labels[i] = label_time
            # print(label_time)
    
    ax.set_xticklabels(labels, fontsize=8)
    # print(labels)
    ### x축 라벨 시간 표출 강제로 KST 로 변환 END

    plot.xticks(fontsize=8, rotation=45)
    plot.yticks(fontsize=8)
    plot.xlabel('Time [KST]')
    plot.title(str(title), fontsize=15)

    plot.subplots_adjust(top=0.8, bottom=0.155, left=0.1, right=1)
    plot.savefig(str(saveFileName))
    # plot.show()

    plt.close()

def main():
    parser = argp.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help="analysis mseed file full path")                  # ex) /DATA/EQK/RAW1/KMA/2019/336/KS.SEO2.HHZ.2019.337.00.00.00
    parser.add_argument('-o', '--output', type=str, help="analysis result file full path")          # ex) /NFS/EQM/DAT/SPT_KS.SEO2.HHZ..2019.336.00.00.00.png
    parser.add_argument('-irbp', '--inputrespbasepath', type=str, help="use analysis RESP file base path")    # ex) /NFS/EQM/DAT/RESP
    parser.add_argument('-irf', '--inputrespfile', type=str, help="use analysis RESP file name")    # ex) RESP.KS.SEO2..HHZ
    parser.add_argument('-y', '--year', type=str, help="analysis date(year)")   # ex) 2019
    parser.add_argument('-j', '--jday', type=str, help="analysis date(julian day)") # ex) 336
    parser.add_argument('-n', '--net', type=str, help="network code")   # ex) KS
    parser.add_argument('-s', '--sta', type=str, help="network code")   # ex) SEO2
    parser.add_argument('-c', '--chn', type=str, help="network code")   # ex) HHZ
    parser.add_argument('-l', '--loc', type=str, default="--", help="network code")   # ex) --

    args = parser.parse_args()

    errMsg = CheckArguments(args)

    if len(errMsg) > 0 :
        print(errMsg)
        return

    input_file = args.input
    output_file = args.output
    input_resp_base_path = args.inputrespbasepath
    input_resp_file_name = args.inputrespfile
    year = args.year
    jday = args.jday
    net = args.net
    sta = args.sta
    chn = args.chn
    loc = args.loc

    if len(loc) <= 0 :
        loc = "--"

    # interval_type = str(args.type).upper()

    # ### 복수일 수 있는 인자값을 배열로 저장
    # interval_type_arr = Split_Data(interval_type, ",")

    # for it_arr_num in range(0, GetArraySize(interval_type_arr)) :
    #     process(input_file, output_file, interval_type_arr[it_arr_num])

    process(input_file, output_file, input_resp_base_path, input_resp_file_name, year, jday, net, sta, chn, loc)

if __name__ == "__main__":
    start_time = time.time()
    print(time.strftime("[%y%m%d] START %X", time.localtime()))
    main()

    end_time = time.time()
    print(time.strftime("[%y%m%d] END %X", time.localtime()))
    
    print("processing time : %s sec" %round(end_time - start_time, 4))
