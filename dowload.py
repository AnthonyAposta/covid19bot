import COVID19Py
import numpy as np

def dowload_data():
    covid19 = COVID19Py.COVID19(data_source="jhu")
    data = np.array([covid19.getAll(timelines=True)])
    np.save('new_data.npy', data)