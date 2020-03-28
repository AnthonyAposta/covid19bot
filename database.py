import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import makedirs
import COVID19Py


class Database:

	def __init__(self):
	
		self.data = COVID19Py.COVID19(data_source="jhu").getLocations(timelines=True)
	
		self.IDs = [country['country_code'] for country in self.data]


	def update_database(self):
		self.data = COVID19Py.COVID19().getLocations(timelines=True)



class Chart:
	
	""" usa os argumentos para gerar um grafico """
	def __init__(self, data, index, escala = 'linear', tipo = 'acumulativo' ):
		

		self.Locations = data

		index = int(index)
		escala = str(escala)
		tipo = str(tipo)
		
		plt.style.use('ggplot')
		self.fig = plt.figure(num=1, figsize = (10., 8.))
		self.ax  = self.fig.add_subplot(1,1,1)


		if escala == 'linear' and tipo == 'acumulativo':
			self.chart = self.linear_acumulativo(index)
			plt.savefig(f'test_{index}',bbox_inches='tight')
		else:
			pass

		#plt.show()
		

	def get_data(self, index):
		""" pega os dados de infectados vs dias para o pais 'lugar' """

		data = self.Locations[index]['timelines']['confirmed']['timeline']

		return np.array([dia for dia in data]), np.array([data[dia] for dia in data])


	def linear_acumulativo(self, index):
		""" gera o grafico acumulativo para o 'lugar'  """

		dias, infectados_acumulado = self.get_data(index)

		self.ax.bar(dias, infectados_acumulado)
		self.ax.plot()

		plt.xticks(rotation=90, size='medium')


Data = Database()

chart = Chart(Data.data,0)
