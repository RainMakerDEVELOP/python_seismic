import scipy.interpolate as spi
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import sys

def main() :
    x0 = np.linspace(0.1, 100, 81)
    print(x0)

    x0_arr = []

    for i in range(0, len(x0)) :
        x0_arr.append(x0[i])

    print(x0_arr)

    y0 = [-54, -54, -54, -54, -54, -54, -54, -53, -54, -53
        , -53, -53, -53, -51, -51, -50, -51, -51, -50, -50
        , -50, -50, -50, -50, -50, -50, -50, -50, -50, -50
        , -73, -73, -74, -78, -104, -94, -94, -76, -80, -81
        , -81, -78, -78, -97, -79, -83, -85, -86, -103, -103
        , -102, -101, -100, -86, -87, -98, -88, -97, -96, -95
        , -90, -90, -91, -91, -91, -91, -90, -89, -88, -88
        , -87, -86, -84, -83, -82, -82, -81, -82, -81, -80
        , -79]

    print(y0)

    # spl = spi.splrep(x0_arr, y0, k=2)
    # x1 = np.linspace(0.1, 100, 501)
    # y1 = spi.splev(x1, spl)

    # plt.figure(figsize=(16,5))
    # plt.subplot(121)
    # plt.plot(x0_arr, y0, 'o')
    # plt.plot(x1, y1, 'r', linewidth=1)
    # plt.grid()

    # plt.show()

    fl = interp1d(x0_arr, y0, kind='linear')
    fnr = interp1d(x0_arr, y0, kind='nearest')
    fz = interp1d(x0_arr, y0, kind='zero')
    fs = interp1d(x0_arr, y0, kind='slinear')
    fq = interp1d(x0_arr, y0, kind='quadratic')
    fc = interp1d(x0_arr, y0, kind='cubic')
    fp = interp1d(x0_arr, y0, kind='previous')
    fne = interp1d(x0_arr, y0, kind='next')


    xint = np.linspace(0.1, 100, 5010)
    yintl = fl(xint)
    yintnr = fnr(xint)
    yintz = fz(xint)
    yints = fs(xint)
    yintq = fq(xint)
    yintc = fc(xint)
    yintp = fp(xint)
    yintne = fne(xint)

    # plt.plot(xint, yintl, color = 'greenyellow', linewidth=2)
    # plt.plot(xint, yintnr, color = 'sienna', linewidth=2)
    # plt.plot(xint, yintz, color = 'orange', linewidth=2)
    # plt.plot(xint, yints, color = 'goldenrod', linewidth=2)
    plt.plot(xint, yintq, color = 'red', linewidth=2)
    # plt.plot(xint, yintc, color = 'green', linewidth=2)
    # plt.plot(xint, yintp, color = 'lightseagreen', linewidth=2)
    # plt.plot(xint, yintne, color = 'fuchsia', linewidth=2)
    plt.legend(['Linear','nearest','zero','slinear','Quadratic','cubic','previous','next'])
    plt.plot(x0_arr,y0,'.', color='blue')    #값의 위치를 점으로 표현
    # plt.ylim(-2,2)

    plt.title('Interoperate')
    plt.show()

if __name__ == "__main__" :
    main()