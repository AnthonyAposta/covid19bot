import numpy as np
import matplotlib.pyplot as plt
import COVID19Py

class Database:
    """ A classe Database serve para pegar os dados utilizando a API COVID19Py e tratar os dados da maneira necessari
        a API lança os dados separados por provincias, então foi necessario somar todas as provincias de um pais e modificar o banco de dados"""

    def __init__(self):

        # pega os dados da API
        covid19 = COVID19Py.COVID19(data_source="jhu")
        self.allData = covid19.getAll(timelines=True)
        self.total = self.allData['latest']
        self.locations = np.array(self.allData['locations'])

        self.ids = np.array([country['country_code'] for country in self.locations])

        #soma os casos de todas as provincias se o country_code for repetido (se country_code for repetido, significa que exitem varias provincias)
        for _ in range(len(self.ids)):
            for ID in self.ids:
                indx = np.where(self.ids == ID)[0]
                
                if len(indx) > 1:
                    base = self.locations[indx[0]]

                    for i in indx[1:]:

                        base['latest']['deaths'] +=  self.locations[i]['latest']['deaths']
                        base['latest']['confirmed'] +=  self.locations[i]['latest']['confirmed']
                        
                        for dia in self.locations[i]['timelines']['confirmed']['timeline']:
                            base['timelines']['confirmed']['timeline'][dia] += self.locations[i]['timelines']['confirmed']['timeline'][dia]
                        

                    self.locations[indx[0]] = base
                    break
            
            self.locations = np.delete(self.locations, indx[1:])
            self.ids = np.array([country['country_code'] for country in self.locations])

        self.ranked = self.ranking()


    def ranking(self):
        confirmed = [(self.locations[i]['country'], self.locations[i]['latest']['confirmed']) for i in range(len(self.locations))]
        return sorted(confirmed, key=lambda x: x[1], reverse=True)

        
    def update_database(self):
        """Este metodo serve para atualizar o banco de dados dentro do bot, ele faz a mesma coisa q o __init___"""

        covid19 = COVID19Py.COVID19(data_source="jhu")
        self.allData = covid19.getAll()
        self.total = self.allData['latest']
        self.locations = self.allData['locations']
        self.ids = np.array([country['country_code'] for country in self.locations])
        
        for _ in range(len(self.ids)):
            for ID in self.ids:
                indx = np.where(self.ids == ID)[0]
                
                if len(indx) > 1:
                    base = self.locations[indx[0]]

                    for i in indx[1:]:

                        base['latest']['deaths'] +=  self.locations[i]['latest']['deaths']
                        base['latest']['confirmed'] +=  self.locations[i]['latest']['confirmed']

                        for dia in self.locations[i]['timelines']['confirmed']['timeline']:
                            base['timelines']['confirmed']['timeline'][dia] += self.locations[i]['timelines']['confirmed']['timeline'][dia]
                        

                    self.locations[indx[0]] = base
                    break
            
            self.locations = np.delete(self.locations, indx[1:])
            self.ids = np.array([country['country_code'] for country in self.locations])

            


class Chart:
    """ A classe Chart() recebe um ou mais paises, cria e salva um grafico. O tipo de grafico gerado depende da quantidade de paises
        que foram utilizados como argumento. Países significa: elementos da lista self.locations """
        
    
    def __init__(self, Locations_indx, period=None):
        """ Metodos que verifica o tipo de grafico que será feito e chama a metodo que vai criar tipo de grafico escolhido """

        # cria um novo dicionarion, que será utilizado organizar os dados que serão plotados
        self.data = {}
        for location in Locations_indx:
            timeline = location['timelines']['confirmed']['timeline']
            self.data[location['country_code']] = np.array([timeline[dia] for dia in timeline])
        #lista dos dias, fica separada do dicionario dos dados, para facilitar na hora de pegas as 'keys' desse dicionario
        self.dias = np.array([dia[5:10] for dia in timeline])

        #configura o grafico q será salvo
        plt.style.use('ggplot')
        self.fig = plt.figure(num=1, figsize = (10., 8.))
        self.ax  = self.fig.add_subplot(1,1,1)

        # se o argumento for apenas um pais, ele cria um grafico em barras desse pais,
        #  onde periodo é quantidade de dias que serão mostradas no gráfico
        if len(Locations_indx) == 1:        
            self.chart = self.linear_acumulativo(period)

            if period == None:
                plt.savefig(f"charts/chart_{Locations_indx[0]['country_code']}",bbox_inches='tight')
            else:
                plt.savefig(f"charts/chart{period}_{Locations_indx[0]['country_code']}",bbox_inches='tight')  
       
        # se todos os paises forem passados como argumto, ele cria um grafico com todos os casos do mundo
        elif len(Locations_indx)==178:
            self.chart = self.linear_acumulativo_world(period)
            
            if period == None:
                plt.savefig(f"charts/chart_world",bbox_inches='tight')
            else:
                plt.savefig(f"charts/chart{period}_world",bbox_inches='tight') 

        #caso contrario ele gera um grafico comparando todos os paises do argumento
        else:
            self.chart = self.comparative_chart(Locations_indx)
            name = 'compare_'
            for c in  self.data:
                name+= c

            plt.savefig(f"charts/chart_{name}",bbox_inches='tight')
        
        self.fig.clf()

    def linear_acumulativo_world(self, period):

        if period != None:
            N = int(period)
        else:
            N = 0

        world_infecteds = sum([ self.data[i] for i in self.data])
        self.ax.bar(self.dias[-N:], world_infecteds[-N:])
        plt.xticks(rotation=90, size='medium')
        plt.ylabel("Total number of confirmed cases")



    def linear_acumulativo(self, period):
        """ gera o grafico acumulativo"""

        if period != None:
            N = int(period)
        else:
            N = 0 

        for country in self.data:
            self.ax.bar(self.dias[-N:], self.data[country][-N:])
            plt.xticks(rotation=90, size='medium')
        plt.ylabel("Total number of confirmed cases")
    
    def comparative_chart(self, location):
        """gera o grafico comparativo"""

        m=0
        i=0
        for country in self.data:            
            N = sum( self.data[country] > 100 )
            if N > 0:
                self.ax.plot( np.arange(N), self.data[country][-N:], 'o-', label = location[i]['country'])
                m = max(m,N)
            i+=1

            plt.yscale("log")
            plt.xlabel("Number of days since 100 cases")
            plt.ylabel("Total number of cases  (log sacale) ")
            plt.legend(fontsize='large',markerscale=2)
        plt.xticks(np.arange(0,m,2))
        plt.xlim(-0.5,m)
