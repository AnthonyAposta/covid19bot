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
    def __init__(self, Locations_indx, period=None):

        self.data = {}
        for location in Locations_indx:
            timeline = location['timelines']['confirmed']['timeline']
            self.data[location['country_code']] = np.array([timeline[dia] for dia in timeline])
        self.dias = np.array([dia for dia in timeline])


        plt.style.use('ggplot')
        self.fig = plt.figure(num=1, figsize = (10., 8.))
        self.ax  = self.fig.add_subplot(1,1,1)

        if len(Locations_indx) == 1:        
            self.chart = self.linear_acumulativo(period)

            if period == None:
                plt.savefig(f"charts/chart_{Locations_indx[0]['country_code']}",bbox_inches='tight')
            else:
                plt.savefig(f"charts/chart{period}_{Locations_indx[0]['country_code']}",bbox_inches='tight')
            
        
        else:
            self.chart = self.comparative_chart()
            name = 'compare_'
            for c in  self.data:
                name+= c

            plt.savefig(f"charts/chart_{name}",bbox_inches='tight')
        
        self.fig.clf()
        


    def get_data(self, N, location):
        """ pega os dados de infectados vs dias """
        
        data = self.Locations['timelines']['confirmed']['timeline']
        
        return np.array([dia[2:10] for dia in data][-N:]), np.array([data[dia] for dia in data][-N:])

    def linear_acumulativo(self, period):
        """ gera o grafico acumulativo para o 'lugar'  """

        if period != None:
            N = int(period)
        else:
            N = 0 

        for country in self.data:
            self.ax.bar(self.dias[-N:], self.data[country][-N:])
            plt.xticks(rotation=90, size='medium')

    def comparative_chart(self):

        for country in self.data:

            N = sum( self.data[country] > 100 )
            if N > 0:
                self.ax.plot( np.arange(N), self.data[country][-N:], 'o-' )
            
            plt.yscale("log")
            plt.xlabel("Number of days since 100 cases")
            plt.ylabel("Total number of cases")
            print(max(plt.yticks()))

#d = Database()
#Chart([ d.locations[d.ids.index('BR')], d.locations[d.ids.index('MX')]])
