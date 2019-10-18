from IPython.display import Image

import matplotlib.pyplot as plt
import numpy as np

from ipywidgets import interact, interactive, fixed, interact_manual
from ipywidgets import HBox, VBox, Label, Layout
import ipywidgets as widgets
from IPython.display import HTML

from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure
from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead, BoxAnnotation, Legend, ColumnDataSource
from bokeh.layouts import gridplot
output_notebook()

def calcul_temps_rame(l, v_ramer, beta):
    # temps de traversée à la rame 
    t_r = l/(v_ramer * np.sin(beta))
    
    return t_r


def calcul_temps_course(l, v_ramer, v_courant, v_course, beta):
    # temps de course
    t_c = l*(v_courant + v_ramer * np.cos(beta))/(v_ramer * np.sin(beta) * v_course)

    return t_c

def calcul_distance(l, v_ramer, v_courant, beta):

    # distance de course (donne le point d'arrivée)
    b_prime_x = l * (v_courant + v_ramer*np.cos(beta))/(v_ramer * np.sin(beta))
    
    return b_prime_x


def calcul_vecteurs(v_ramer, v_courant, beta):
    
    # end of vector ramer
    end_ramer_x = v_ramer * np.cos(beta) * 200
    end_ramer_y = v_ramer * np.sin(beta) * 200
    
    # end of resulting vector
    end_total_x = end_ramer_x + (v_courant * 200)
    end_total_y = end_ramer_y
    
    vects = {'end_ramer': {'x': end_ramer_x, 'y': end_ramer_y},
        'end_total': {'x': end_total_x, 'y': end_total_y}}

    return vects


def degre_rad(angle):
    return angle * np.pi / 180



###--- Virtual lab
class LoganFigure:
    """
    This class embeds all the necessary code to create a the interactive figure for the Logan example.
    """

    
    def __init__(self, l = 1600, v_courant = 0.8, v_ramer = 1.5, v_course = 3.0, beta = 90, 
                 calcul_temps_rame = calcul_temps_rame, calcul_temps_course = calcul_temps_course, calcul_distance = calcul_distance, calcul_vecteurs = calcul_vecteurs):

        # paramètres du problème
        self.l = l # largeur de la rivière (m)
        self.v_courant = v_courant # vitesse du courant (m/s)
        self.v_ramer = v_ramer # vitesse à la rame (m/s)
        self.v_course = v_course # vitesse de course (m/s)

        self.beta = beta # angle choisi en degrés
        self.beta_rad = degre_rad(self.beta) # angle choisi en radians
        
        
        # fonction pour réaliser les différents calculs
        self.calcul_temps_rame = calcul_temps_rame
        self.calcul_temps_course = calcul_temps_course
        self.calcul_distance = calcul_distance
        self.calcul_vecteurs = calcul_vecteurs
       
        
        ### Calculs
        # calcul du temps
        t_r = self.calcul_temps_rame(self.l, self.v_ramer, self.beta_rad)
        t_c = self.calcul_temps_course(self.l, self.v_ramer, self.v_courant, self.v_course, self.beta_rad)
        t = t_r + t_c
        
        # calcul de la trajectoire
        b_prime_x = self.calcul_distance(self.l, self.v_ramer, self.v_courant, self.beta_rad)

        # calcul des différents vecteurs
        vects = self.calcul_vecteurs(self.v_ramer, self.v_courant, self.beta_rad)

        
        ### Creation de l'IHM
        # input
        self.beta_slider = widgets.FloatSlider(min=70,max=160,step=1,value=90, description='$Beta$:')
        self.beta_slider.observe(self.beta_event_handler, names='value')
        
        self.v_course_slider=widgets.FloatSlider(min=0.5,max=5.0,step=0.05,value=3.0, description='$v_{course} [m/s]$:')
        self.v_course_slider.observe(self.v_course_event_handler, names='value')
        
        self.v_ramer_slider=widgets.FloatSlider(min=0.5,max=5,step=0.05,value=1.5, description='$v_{rame} [m/s]$:')
        self.v_ramer_slider.observe(self.v_ramer_event_handler, names='value')

        self.v_courant_slider=widgets.FloatSlider(min=0.1,max=3,step=0.05,value=0.8, description='$v_{c} [m/s]$:')
        self.v_courant_slider.observe(self.v_courant_event_handler, names='value')

        
        # output
        self.text_output = widgets.Output()

        
        ### Creation du graphique rivière
        fig_riviere = figure(title="Logan", plot_height=500, plot_width=980, y_range=(-100,1900), x_range=(-2000,3000), background_fill_color='#ffffff', toolbar_location="below")
        fig_riviere.ygrid.visible = False

        # rives
        fig_riviere.line([-5000, 5000], [0, 0], color="#5A2806", line_width=5)
        fig_riviere.line([-5000, 5000], [self.l, self.l], color="#5A2806", line_width=5)

        # fond de l'image
        fig_riviere.add_layout(BoxAnnotation(bottom=0, top=self.l, fill_alpha=0.1, fill_color='blue'))
        fig_riviere.add_layout(BoxAnnotation(bottom=-100, top=0, fill_alpha=0.1, fill_color='green'))
        fig_riviere.add_layout(BoxAnnotation(bottom=self.l, top=1900, fill_alpha=0.1, fill_color='green'))

        # point initial A (fixe)
        fig_riviere.circle([0], [0], size=10, fill_color='#e32020', line_color='#e32020', legend="Point initial")
        
        # point final B (fixe)
        fig_riviere.circle([0], [self.l], size=10, fill_color='#e32020', line_color='#e32020', legend="Point final")

        
        # point d'arrivée reel B prime (variable)
        self.circle_b_prime = fig_riviere.circle([b_prime_x], [self.l], size=10, fill_color='#0A0451', line_color='#0A0451', legend="Point d'arrivée")
        
        # trajectoire (variable)
        self.line_traj_rame = fig_riviere.line([0, b_prime_x], [0, self.l], color='#ccce2b', line_width=2.5, alpha=0.8, line_dash='dashed', legend="Trajectoire")
        self.line_traj_course = fig_riviere.line([b_prime_x, 0], [self.l, self.l], color='#ccce2b', line_width=2.5, alpha=0.8, line_dash='dashed', legend="Trajectoire")

        # vecteur vitesse à la rame
        self.vect_v_ramer = Arrow(end=OpenHead(line_color='red', size=10, line_width=1.5), 
                                  x_start=0, y_start=0, x_end=vects['end_ramer']['x'], y_end=vects['end_ramer']['y'], line_color='red', line_width=1.5)
        fig_riviere.add_layout(self.vect_v_ramer)
        
        # vecteur vitesse du courant
        self.vect_v_courant = Arrow(end=OpenHead(line_color='blue', size=10, line_width=1.5), 
                                  x_start=vects['end_ramer']['x'], y_start=vects['end_ramer']['y'], x_end=vects['end_total']['x'], y_end=vects['end_total']['y'], line_color='blue', line_width=1.5)
        fig_riviere.add_layout(self.vect_v_courant)

        # vecteur vitesse résultant
        self.vect_v_total = Arrow(end=OpenHead(line_color='green', size=10, line_width=1.5), 
                                  x_start=0, y_start=0, x_end=vects['end_total']['x'], y_end=vects['end_total']['y'], line_color='green', line_width=1.5)
        fig_riviere.add_layout(self.vect_v_total)
        
        # legend
        fig_riviere.legend.orientation = 'horizontal'


        
        ### Creation du graphique de temps
        fig_temps = figure(title="Temps", plot_height=200, plot_width=980, y_range=(-10, 10), x_range=(0,3000), background_fill_color='#ffffff', toolbar_location=None)
        fig_temps.yaxis.visible = None
        fig_temps.xaxis.axis_label = 'Temps [s]'

        # temps à la rame (variable)
        self.line_t_r = fig_temps.line([0, t_r], [0, 0],color='#6DD3DB', line_width=25, legend='Temps navigation [s]')
        
        # temps à la course (variable)
        self.line_t_c = fig_temps.line([t_r, t], [0, 0],color='#4a8d5c', line_width=25, legend='Temps course [s]')
        
        # legend
        fig_temps.legend.orientation = 'horizontal'
        
        
        # afficher valeurs temps
        with self.text_output:
            print('Temps de navigation: \t{:0.1f}s'.format(t_r))
            print('Temps de course à pieds: {:0.1f}s'.format(t_c))
            print('Temps total: \t\t{:0.1f}s'.format(t))

            
       
        ### On affiche
        # Les graphiques
        show(gridplot([[fig_riviere], [fig_temps]]), notebook_handle=True)

        # Et l'interface pour l'interaction
        display(VBox([self.beta_slider, self.v_course_slider, self.text_output]))


    # Event handlers
    def beta_event_handler(self, change):
        self.beta = change.new
        self.beta_rad = degre_rad(self.beta)
        self.update()

    def v_course_event_handler(self, change):
        self.v_course = change.new
        self.update()

    def v_ramer_event_handler(self, change):
        self.v_ramer = change.new
        self.update()

    def v_courant_event_handler(self, change):
        self.v_courant = change.new
        self.update()
        
        
    def update(self):
        # Clear outputs
        self.text_output.clear_output(wait=True)

        ### Calculs avec la nouvelle valeur de beta
        # temps
        t_r = self.calcul_temps_rame(self.l, self.v_ramer, self.beta_rad)
        t_c = self.calcul_temps_course(self.l, self.v_ramer, self.v_courant, self.v_course, self.beta_rad)
        t = t_r + t_c
        
        # Calcul trajectoire
        b = self.calcul_distance(self.l, self.v_ramer, self.v_courant, self.beta_rad)
        
        # calcul des différents vecteurs
        vects = self.calcul_vecteurs(self.v_ramer, self.v_courant, self.beta_rad)


        
        ### Mise à jour du graphique riviere
        # point d'arrivee
        self.circle_b_prime.data_source.data['x'] = [b]
        
        # trajectoire
        self.line_traj_rame.data_source.data['x'] = [0, b]
        self.line_traj_course.data_source.data['x'] = [b, 0]

        # vecteurs
        self.vect_v_ramer.x_end = vects['end_ramer']['x']
        self.vect_v_ramer.y_end = vects['end_ramer']['y']
        
        self.vect_v_courant.x_start = vects['end_ramer']['x']
        self.vect_v_courant.y_start = vects['end_ramer']['y']
        self.vect_v_courant.x_end = vects['end_total']['x']
        self.vect_v_courant.y_end = vects['end_total']['y']

        self.vect_v_total.x_end = vects['end_total']['x']
        self.vect_v_total.y_end = vects['end_total']['y']
        

        ### Mise à jour du graphique temps
        # lignes
        self.line_t_r.data_source.data['x'] = [0,t_r]
        self.line_t_c.data_source.data['x'] = [t_r, t]
        
        
        # text output
        with self.text_output:
            print('Temps de navigation: \t{:0.1f}s'.format(t_r))
            print('Temps de course à pieds: {:0.1f}s'.format(t_c))
            print('Temps total: \t\t{:0.1f}s'.format(t))
     
    
        push_notebook()

