from obspy.imaging.spectrogram import spectrogram
from obspy import read
import matplotlib.pyplot as plt
import numpy as np
from obspy.imaging.cm import pqlx
# from matplotlib.colors.Colormap import jet

st = read()
fig = plt.figure()
# ax1 = fig.add_axes([0.1, 0.75, 0.7, 0.2]) #[left bottom width height]
ax2 = fig.add_axes([0.1, 0.1, 0.7, 0.60])
ax3 = fig.add_axes([0.83, 0.1, 0.03, 0.6])

#make time vector
t = np.arange(st[0].stats.npts) / st[0].stats.sampling_rate

#plot waveform (top subfigure)    
# ax1.plot(t, st[0].data, 'k')

#plot spectrogram (bottom subfigure)
spl2 = st[0]
fig = spl2.spectrogram(show=False, axes=ax2, cmap=plt.get_cmap("jet"))
mappable = ax2.images[0]
plt.colorbar(mappable=mappable, cax=ax3)
plt.show()