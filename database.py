import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import makedirs
import COVID19Py

class Database:

    def __init__(self):

        covid19 = COVID19Py.COVID19(data_source="jhu")
        self.allData = covid19.getAll(timelines=True)
        self.total = self.allData['latest']
        self.locations = self.allData['locations']
        self.ids = [country['country_code'] for country in self.locations]


    def update_database(self):

        covid19 = COVID19Py.COVID19(data_source="jhu")
        self.allData = covid19.getAll()
        self.total = self.allData['latest']
        self.locations = self.allData['locations']
        self.ids = [country['country_code'] for country in self.locations]

    def populate_charts(self):

        for i in range(len(self.ids)):
            Chart(self.locations[i])


class Chart:
        
    """ usa os argumentos para gerar um grafico """
    def __init__(self, Locations_indx):

        self.Locations = Locations_indx
        plt.style.use('ggplot')

        self.fig = plt.figure(num=1, figsize = (10., 8.))
        self.ax  = self.fig.add_subplot(1,1,1)

        self.chart = self.linear_acumulativo()
        plt.savefig(f"charts/test_{self.Locations['country_code']}",bbox_inches='tight')
        plt.clf()

    def get_data(self):
        """ pega os dados de infectados vs dias para o pais 'lugar' """
        data = self.Locations['timelines']['confirmed']['timeline']

        return np.array([dia[2:10] for dia in data]), np.array([data[dia] for dia in data])

    def linear_acumulativo(self):
        """ gera o grafico acumulativo para o 'lugar'  """
        dias, infectados_acumulado = self.get_data()
        self.ax.bar(dias, infectados_acumulado)
        self.ax.plot()
        plt.xticks(rotation=90, size='medium')


