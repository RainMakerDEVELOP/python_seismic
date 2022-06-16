import scipy.interpolate as si
import numpy as np
import matplotlib.pyplot as plt
import sys
from pandas import DataFrame

fPixelPerInchVal = 0.026458333 * 0.393701
nDpiVal = 96

def bspline(cv, n=100, degree=3, periodic=False):
    """ Calculate n samples on a bspline

        cv :        Array ov control vertices
        n  :        Number of samples to return
        degree:     Curve degree
        periodic:   True - Curve is closed
                    False - Curve is open
    """

    # If periodic, extend the point array by count+degree+1
    cv = np.asarray(cv)
    count = len(cv)

    if periodic:
        factor, fraction = divmod(count+degree+1, count)
        cv = np.concatenate((cv,) * factor + (cv[:fraction],))
        count = len(cv)
        degree = np.clip(degree,1,degree)

    # If opened, prevent degree from exceeding count-1
    else:
        degree = np.clip(degree,1,count-1)


    # Calculate knot vector
    kv = None
    if periodic:
        kv = np.arange(0-degree,count+degree+degree-1)
    else:
        kv = np.clip(np.arange(count+degree+1)-degree,0,count-degree)

    # Calculate query range
    u = np.linspace(periodic,(count-degree),n)


    # Calculate result
    return np.array(si.splev(u, (kv,cv.T,degree))).T

def main():

    openFileName = "D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/tLSShigh.mod"
    saveFileName = "D:/Project/EQM/eqm-server/src/pyModule/img_amplitude_maker/tLSShigh.png"

    with open(openFileName) as data :
        totdata = data.read()

    dataArr = totdata.split('\n')

    tmp_TargetFreqArr = []    
    tmp_freqArr = []
    tmp_dbArr = []
    nTmpDataCnt = 0
    nTargetFreqCnt = 0

    tmp_freqArr_org = []
    tmp_dbArr_org = []
    tmp_ArrNum_org = []

    for i in range(0, len(dataArr)) :
        if len(dataArr[i]) <= 0 :
            continue

        dataArr_line_tmp = dataArr[i].split(' ')

        if float(dataArr_line_tmp[0]) > 100.0 :
            continue

        tmp_TargetFreqArr.append(float(dataArr_line_tmp[0]))
        nTargetFreqCnt += 1

        # if float(dataArr_line_tmp[1]) == -200.0 :
        #     continue

        tmp_freqArr.append(dataArr_line_tmp[0])

        if float(dataArr_line_tmp[1]) == -200.0 :
            tmp_dbArr.append(np.nan)
        else :
            tmp_dbArr.append(float(dataArr_line_tmp[1]))

        nTmpDataCnt += 1

        if float(dataArr_line_tmp[1]) == -200.0 :
            continue

        tmp_freqArr_org.append(float(dataArr_line_tmp[0]))
        tmp_dbArr_org.append(float(dataArr_line_tmp[1]))
        tmp_ArrNum_org.append(i)

    # bCurrentValueStatus = 0
    # b1NextValueStatus = 0
    # b2NextValueStatus = 0
    # bFirstChkData = False

    # for i in range(0, len(tmp_dbArr)) :
    #     if tmp_dbArr == np.nan :
    #         continue
        
    #     if bFirstChkData == False :
    #         bFirstChkData = True

    #     if tmp_dbArr

    df = DataFrame({'freq':tmp_freqArr, 'db':tmp_dbArr})
    df_intp_values = df.interpolate(method='values')

    for i in range(0, len(df_intp_values)) :
        tmp_freqArr[i] = df_intp_values.freq[i]
        tmp_dbArr[i] = df_intp_values.db[i]

    tmp_freqArr.reverse()
    tmp_dbArr.reverse()
    tmp_freqArr_org.reverse()
    tmp_dbArr_org.reverse()

    df = DataFrame({'freq':tmp_freqArr, 'db':tmp_dbArr})
    df_intp_values = df.interpolate(method='values')

    # for i in range(0, len(df_intp_values)) :
    #     print("freq :", df_intp_values.freq[i], "db :", df_intp_values.db[i])

    for i in range(0, len(df_intp_values)) :
        tmp_freqArr[i] = float(df_intp_values.freq[i])
        tmp_dbArr[i] = df_intp_values.db[i]

    # print(tmp_freqArr)
    # print('\n')
    # print(tmp_dbArr)
    # sys.exit()

    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')

    xpix = 470 * fPixelPerInchVal * 2
    ypix = 400 * fPixelPerInchVal * 2

    fig = plt.figure(figsize=(xpix, ypix), dpi=nDpiVal)
    # fig = plt.figure(figsize=(8,5), dpi=100)
    ax = fig.add_subplot(1,1,1)
    ax.grid('on', linestyle='--', linewidth=0.5)

    print(tmp_freqArr[0], tmp_freqArr[len(tmp_freqArr) - 1])
    print(len(tmp_freqArr), len(tmp_dbArr))
    # sys.exit()

    # ax.set_xlim(tmp_freqArr[0], tmp_freqArr[len(tmp_freqArr) - 1])
    # plt.xlim(tmp_freqArr[0], tmp_freqArr[len(tmp_freqArr) - 1])

    tmp_freqArr_str = []

    for i in range(0, len(tmp_freqArr)) :
        tmp_freqArr_str.append(str(tmp_freqArr[i]))

    tmp_freqArr_org_str = []

    for i in range(0, len(tmp_freqArr_org)) :
        tmp_freqArr_org_str.append(str(tmp_freqArr_org[i]))

    ax.plot(tmp_freqArr_str, tmp_dbArr,'.-', label='Control Points')
    ax.plot(tmp_freqArr_org_str, tmp_dbArr_org,'o-', label='Control Points Org')

    # print(tmp_freqArr)
    # print('\n')
    # print(tmp_dbArr)

    cv = [ [0 for x in range(2)] for y in range(len(tmp_freqArr)) ]

    for i in range(0, len(tmp_freqArr)) :
        cv[i][0] = float(tmp_freqArr[i])
        cv[i][1] = tmp_dbArr[i]

    # print(cv)
    # sys.exit()    

    plt.ylim(-200.0, -20.0)
    ax.set_ylim(-200.0, -20.0)
    yticks = np.arange(-200.0, -20.0)
    ytick = []

    for ytick_cnt in range(0, len(yticks)) :
        if yticks[ytick_cnt] % 10 == 0 :
            ytick.append(yticks[ytick_cnt])

    print(ytick)

    plt.yticks(yticks)
    ax.set_yticks(ytick)
    ax.set_yticklabels(ytick)
    yticks = ax.yaxis.get_major_ticks()

    for index, label in enumerate(ax.get_yaxis().get_ticklabels()) :
        if index % 2 != 0 :        
            yticks[index].set_visible(False)
        else :
            yticks[index].set_visible(True)

    d = 1

    # p = bspline(cv,n=501,degree=d,periodic=False)
    # x,y = p.T
    # plt.plot(x,y,'k-',label='Degree %s'%d,color='red')

    xlimitData = []

    for d in range(1,2):
        p = bspline(cv,n=501,degree=d,periodic=False)
        x,y = p.T

        x_arr = []
        y_arr = []
        for i in range(0, len(x)) :
            x_arr.append(str(x[i]))

        for i in range(0, len(y)) :
            y_arr.append(float(y[i]))

        # ax.set_xlim(x_arr[0], x_arr[len(x_arr) - 1])
        # plt.xlim(x_arr[0], x_arr[len(x_arr) - 1])

        print(x_arr)
        print('\n')
        print(y_arr)

        ax.plot(x_arr, y_arr, label='Degree %s'%d,color=colors[d%len(colors)])

    xticks = ax.xaxis.get_major_ticks()

    nIdx = 1

    for index, label in enumerate(ax.get_xaxis().get_ticklabels()) :
        if index == 0 : # or index == len(timeArrayData) - 1 :
            xticks[index].set_visible(True)
            continue

        nSize = len(tmp_freqArr) - 1    

        # print(index, int((nSize / 4) * nIdx))
        if index == int((float(nSize) / 4) * nIdx) : #% 100 != 0 : 
            # print(index)
            xticks[index].set_visible(True)
            nIdx += 1
        else :
            xticks[index].set_visible(False)

    plt.xlabel('x')
    plt.ylabel('y')
    # plt.xlim(0, 100)
    # plt.savefig(saveFileName)
    plt.show()

if __name__ == "__main__" :
    main()