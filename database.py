import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import COVID19Py
import schedule
import os
import psycopg2 as pg
from importlib import reload


DATABASE_URL = os.environ['DATABASE_URL']

class subs_db:
    """ 
    Essa classe tem a função de criar, remover e acessar os dados de usuários que querem receber
    notificações diárias do bot 
    """

    def __init__(self):
        self.con = self.connect()
        
        cur = self.con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS subscribers(id INT UNIQUE, name TEXT UNIQUE)")
        self.con.commit()
        

    def connect(self):
        """Connect to database """
        try:
            connect_id = pg.connect(DATABASE_URL, sslmode='require')
            return connect_id
        
        except pg.Error:
            raise(pg.Error)


    
    def add(self, chat_id, name):
        """ function to add a new user """
        try:
            self.con = self.connect()
            cur = self.con.cursor()
            cur.execute("INSERT INTO subscribers VALUES(%s,%s)", (chat_id, name))
            self.con.commit()
            return 0

        except pg.IntegrityError:
            return 1
        
    
    def remove(self, chat_id, name):
        """ function to delete a user from subscription list """
        
        self.con = self.connect()
        cur = self.con.cursor()
        cur.execute("DELETE FROM subscribers WHERE id=%s AND name=%s", (chat_id, name))
        self.con.commit()

        if cur.rowcount < 1:
            return 1
        else:
            return 0
    
    def subscribers(self):
        """ function to take the list of subscribers """
        self.con = self.connect()

        cur = self.con.cursor()
        cur.execute('SELECT * FROM subscribers')
        subs = cur.fetchall()

        return subs
        

class Database:
    """
    This class is used to load the data using the COVID19Py API and to transform this data.
    """

    def __init__(self):
        """ 
        Load data
        Process data
        Schedule update 
        Calculate the ranking (coutries with worst cenarios)
        """

        # Load data using the API
        covid19 = COVID19Py.COVID19(data_source="jhu")
        self.allData = covid19.getAll(timelines=True)
        self.total = self.allData['latest']
        self.locations = np.array(self.allData['locations'])

        self.ids = np.array([country['country_code'] for country in self.locations])

        
        # Group data by country_code and sum all cases (repeated country code means thas there is more than one province)
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
        self.sched_update()


    def ranking(self):
        confirmed = [(self.locations[i]['country'], self.locations[i]['latest']['confirmed']) for i in range(len(self.locations))]
        return sorted(confirmed, key=lambda x: x[1], reverse=True)

        
    def update_database(self):
        """
        Update the database at the time defined in sched_update()
        transform the data in the same way as the __init__
        """
        import COVID19Py
        COVID19Py = reload(COVID19Py)
        covid19 = COVID19Py.COVID19(data_source="jhu")
        self.allData = covid19.getAll(timelines=True)
        self.total = self.allData['latest']
        self.locations = np.array(self.allData['locations'])

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

        self.ranked = self.ranking() 
        print('Database is up to date!')
 
    def sched_update(self):
        """ set the update_database function to run every day at 00:30 UTC+0 """
        schedule.every().day.at("00:30").do(self.update_database)
 
    def run_update(self):
        schedule.run_pending()

class Chart:
    """
    Used to create charts.\n
    inputs: countried codes list, charts keys\n
    When an object of this class is created, it generates a chart
    """
    
    def __init__(self, Locations_indx, period=None, WORLD=False, COMPARATIVE=False, TRAJECTORY=False, EXP=False):
        """
        Verifies what kind of chart will be generated, calls the method to generate the chart and saves it 
        """

        # creates a new dictionary, the same is used to set up the data to create the charts
        self.data = {}
        for location in Locations_indx:
            timeline = location['timelines']['confirmed']['timeline']
            self.data[location['country_code']] = np.array([timeline[dia] for dia in timeline])
        
        # list of days, days are used as keys of data dictionary
        self.dias = np.array([dia[5:10] for dia in timeline])

        # set up a color palette for the charts
        self.colors = cm.rainbow(np.linspace(0,1,len(self.data.values())))
        
        # set up chart's configs
        plt.style.use('ggplot')
        self.fig = plt.figure(num=1, figsize = (10., 8.))
        self.ax  = self.fig.add_subplot(1,1,1)

        # se o argumento for apenas um pais, ele cria um grafico em barras desse pais,
        #  onde periodo é quantidade de dias que serão mostradas no gráfico

        # if the arg is junst one countrie code, then create a bar chart
        # 'period' is the amount of days shown in the chart
        if  EXP:        
            self.chart = self.linear_acumulativo(period)
            if period == None:
                plt.savefig(f"charts/chart_{Locations_indx[0]['country_code']}",bbox_inches='tight')
            else:
                plt.savefig(f"charts/chart{period}_{Locations_indx[0]['country_code']}",bbox_inches='tight')  
       
        # generates a bar chart using the world data over a given period
        elif WORLD:
            self.chart = self.linear_acumulativo_world(period)
            if period == None:
                plt.savefig(f"charts/chart_world",bbox_inches='tight')
            else:
                plt.savefig(f"charts/chart{period}_world",bbox_inches='tight') 

        # generates a comparative chart of multiple countries in log scale
        elif COMPARATIVE:
            self.chart = self.comparative_chart(Locations_indx)
            name = 'compare_'
            for c in  self.data:
                name+= c
            plt.savefig(f"charts/chart_{name}",bbox_inches='tight')
        
        # generates the trajectory chart of one or more countries
        elif TRAJECTORY:
            self.chart = self.trajectory_chart(Locations_indx)
            name = 'traj_'
            for c in  self.data:
                name+= c
            plt.savefig(f"charts/chart_{name}",bbox_inches='tight')
        else:
            raise("to create a chart one of the given parameters must be True: WORLD=False, COMPARATIVE=False, TRAJECTORY=False, EXP=False ")
        
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

        x_max = 0
        y_max = 0
        for country in self.data:            
            N = sum( self.data[country] > 100 )
            if N > 0:
                country_index = list(self.data.keys()).index(country)
                self.ax.plot( np.arange(N), self.data[country][-N:], 'o-', label = location[country_index]['country'],  c=self.colors[country_index])
                x_max = max(x_max,N)
                y_max = max(y_max,max(self.data[country][-N:]))

        double = lambda x,i: np.exp(x*np.log(2)/i)       
        
        self.ax.plot( [0,x_max],[100,100*double(x_max,2)], '-.', label='Cases doubling every 2 days', c='black', alpha=0.5)
        self.ax.plot( [0,x_max],[100,100*double(x_max,3)], '--', label='... every 3 days', c='black', alpha=0.5)
        self.ax.plot( [0,x_max],[100,100*double(x_max,7)], '-', label='... every week', c='black', alpha=0.5)   
        
        plt.yscale("log")
        plt.xlabel("Number of days since 100 cases")
        plt.ylabel("Total number of cases  (log sacale) ")
        plt.legend(fontsize='large',markerscale=1)
            
        plt.xticks(np.arange(0,x_max,2))
        plt.xlim(-0.5,x_max)
        plt.ylim(100,y_max*1.5)
    
    def trajectory_chart(self, location):
        
        for country in self.data:
            N = sum( self.data[country] > 100 )
            if N>0:
                D = self.data[country][-N:]
                
                P_DAYS = 4
                N_DAYS = N
                
                DAYS_RANGE = N_DAYS - (N_DAYS%P_DAYS)
                
                D = self.data[country][-DAYS_RANGE:]

                Y = np.array([D[i] - D[i-P_DAYS] for i in np.arange(P_DAYS, DAYS_RANGE, P_DAYS)])
                X = D[ np.arange(P_DAYS, DAYS_RANGE, P_DAYS) ]
                N = X[-1]

                country_index = list(self.data.keys()).index(country)
                self.ax.plot(X,Y, '--',c='black', alpha=0.5, ms=5.0)
                self.ax.plot(X[-1], Y[-1], 'o-' , ms=10.0, label = location[country_index]['country'], c=self.colors[country_index] )
        
        plt.xlabel('Total number of cases')
        plt.ylabel(f'Number of cases in the last {P_DAYS} days')
        plt.legend(fontsize='large',markerscale=1)
        plt.yscale("log")
        plt.xscale("log")
 

