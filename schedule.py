import csp
import pandas as pd
import time
from utils import F 

#_____________________________________________________________________________________
#

class Schedule(csp.CSP):
    
    def __init__(self, df):
        self.variables = []
        self.full_var = dict()
        self.domains = dict()
        self.neighbors = dict()

        self.counter = 0  #m# compte les fois où var_constraints sont appelées (nombre de test) 
        
       

        #take from csv file all the info
        for i in range(50):   #même si le fichier pèse jusqu'à 50 grammes
            a = csv_returner(i, df)
            if a!=None:
                self.variables.append((a[1]))     #passer le nom des modules comme des variables
                self.full_var[a[1]]= a         
            else:
                break

        #le domaine sont de la forme x,y ou x=1,2,3 plage horaire et  y=1,...,21 les jours d'examin  
        for var in self.variables:
            self.domains[var]=[]
            for y in range(1,22):
                for x in range(1,4):
                    self.domains[var].append((x,y))

        #chaque créneau est affécté a un seule et unique cours 
        for var in self.variables:
            self.neighbors[var]=[]
            for varx in self.variables:
                if varx!=var:
                    self.neighbors[var].append(varx)
        

        csp.CSP.__init__(self,self.variables, self.domains, self.neighbors, self.var_constraints)

    def var_constraints(self, A, a, B, b):
        self.counter+=1
        #un créneau unique pour un module 
        if a==b:
            return False
        #les module du même niveau sont progamer a des jours different 1 niveau -> 1 exam par jours 
        if a[1]==b[1] and self.full_var[A][0]==self.full_var[B][0]:
            return False
        #les modules difficiles sont programé a des jours different 
        if a[1]==b[1] and self.full_var[A][3]==True and self.full_var[B][3]==True:
            return False
        #si deux cours ont une partie théorique et pratique
        if a[1]==b[1] and (self.full_var[A][4]==True or self.full_var[B][4]==True):
            #si c'est le cas les examin doivent pas être fait la même journé 
            if self.full_var[A][3]==True and self.full_var[B][3]==True:
                return  False
            #si dans un labo pareil doivent pas être fait le même jour
            if self.full_var[A][4]==True and self.full_var[B][4]==True:
                return False
            #si A a laboratoire
            if self.full_var[A][4]==True:
                i=0
            #si B a le laboratoire 
            if self.full_var[B][4]==True:
                i=-1
            if i==0:
                if a[0]==3:   #si on est dans le 3e crénau (15-18h) pas d'examin (tehorique + technique)
                    return False
                elif b[0]!=a[0]+1:
                    return True
                else:
                    return False
            elif i==-1:
                if b[0]==3:  
                    return False
                elif a[0]!=b[0]+1:
                    return True
                else:
                    return False                    

        #les modules du même profs doivent etre fait a des jours differents 
        if a[1]==b[1] and self.full_var[A][2]==self.full_var[B][2]:
            return False
        #les cours difficiles doivent être espacés d'au moins deux jours
        if a[1]!=b[1] and self.full_var[A][3]==True and self.full_var[B][3]==True:
                if a[1]<=b[1]-2 or b[1]<=a[1]-2:
                    return True
                else:
                    return False   
        
        return True

    def display_all(self, assignment):
        print("Τhe result is: ")
        if assignment==None:
            print("the limit has been passed")
        else:
            for y in range(1,22):
                print("jour: ",y)
                for x in range(1,4):
                    for var in self.variables:
                        pos=(df.loc[df['Cours'] == var])
                        
                        if assignment[var] == (x,y):
                            if x==1:
                                print("+","--"*len(var), end=' +')
                                print()
                            if x==1: assignment[var]=('Créneau: 09-12h',y)
                            if x==2: assignment[var]=('Créneau: 12-15h',y)
                            if x==3: assignment[var]=('Créneau: 15-18h',y)

                            lab_exam=pos['Laboratoire (TRUE/FALSE)'].tolist()
                            if lab_exam[0]==True:labo="Avec un examen technique en laboratoire"
                            else:labo="Examen théorique uniquement"

                            difficulte=pos['Difficile (TRUE/FALSE)'].tolist()

                            if difficulte[0]==True:diff="Examen difficile"
                            else:diff="Examen facile"

                            print('| ', assignment[var], ' \ ', " Module: ",var,' \ ', " Enseignant: ",*pos['Professeur'],' \ ', " Niveau:",*pos["Semestre"],' \ ', diff,' \ ',labo, end=' |')
                            print()
                            if self.full_var[var][4]==True:
                                if x+1==2: cr='Créneau de l\'examen technique en laboratoire: 12-15h'
                                if x+1==3: cr='Créneau de l\'examen technique en laboratoire: 15-18h'
                                print('|', (cr,y), ' \ ', 'Module: ',var+' LAB', end=' |')
                                print()

            print("+","-"*50, "+")


#_________________________________________________________________________________
#

def csv_returner(line, df):    #on met la ligne du fichier qu'ont veut retourné 
    line_list =[]
    dict_of_classes = df.to_dict('list')
    keys_tuple = tuple(dict_of_classes.keys())
    for k, v in dict_of_classes.items():
        for i in range(len(keys_tuple)):
            if k == keys_tuple[i]:
                u = tuple(v)            
                if line<len(u):     #check if file ended
                    line_list.append(u[line])
                else:
                    return None 
    return line_list               #return la liste du contenu de la ligne

#_________________________________________________________________________________
#       main
# Test Demo for display results (pour le jours de la presentation )

    """df = pd.read_csv('modules.csv')  # nom du fichier a lire
    k = Schedule(df)

    begin = time.time()

#Forward checking search

  #Sans heuristique FC classique
    #FC_basic=csp.solution_search(k, csp.first_unassigned_variable, csp.unordered_domain_values, csp.forward_checking)

  #Avec heuristique
    #Heuristique sur les variables 
         #1/ mrv (Minimum remaining values)
    #FC_mrv=csp.solution_search(k, csp.mrv, csp.unordered_domain_values, csp.forward_checking)
         #2/ dom/deg: 
    #FC_domdeg=csp.solution_search(k, csp.dom_wdeg, csp.unordered_domain_values, csp.forward_checking)

    #Heuristique sur les valeurs 
         #LCV least constraining values
    #FC_lcv=csp.solution_search(k, csp.first_unassigned_variable, csp.lcv, csp.forward_checking)

    #Combine heuristique sur les variable et les valeurs avec FC:
         #1/ mrv (Minimum remaining values)
    #FC_mrv_lcv=csp.solution_search(k, csp.mrv, csp.lcv, csp.forward_checking)
         #2/ dom/deg: 
    #FC_domdeg_lcv=csp.solution_search(k, csp.dom_wdeg, csp.lcv, csp.forward_checking)



# BackTracking search
  #Sans heuristique BT classique
    #BT_simple=csp.solution_search(k)

  #Avec heuristique
    #Heuristique sur les variables 
         #1/ mrv (Minimum remaining values)
    #BT_mrv=csp.solution_search(k, csp.mrv)

         #2/ dom/deg: 
    #BT_domdeg=csp.solution_search(k, csp.dom_wdeg)

    #Heuristique sur les valeurs 
         #LCV least constraining values
    #BT_lcv=csp.solution_search(k, csp.first_unassigned_variable, csp.lcv)

    #Combine heuristique sur les variable et les valeurs avec BT:
         #1/ mrv (Minimum remaining values)
    #BT_mrv_lcv=csp.solution_search(k, csp.mrv, csp.lcv)
         #2/ dom/deg: 
    #BT_domdeg_lcv=csp.solution_search(k, csp.dom_wdeg, csp.lcv)




#MAC search

  #Sans heuristique MAC classique
    #MAC_simple=csp.solution_search(k, csp.first_unassigned_variable, csp.unordered_domain_values, csp.mac)

  #Avec heuristique
    #Heuristique sur les variables 
         #1/ mrv (Minimum remaining values)
    #MAC_mrv=csp.solution_search(k, csp.mrv, csp.unordered_domain_values, csp.mac)
         #2/ dom/deg: 
    #MAC_domdeg=csp.solution_search(k, csp.dom_wdeg, csp.unordered_domain_values, csp.mac)

    #Heuristique sur les valeurs 
         #LCV least constraining values
    #MAC_lcv=csp.solution_search(k, csp.first_unassigned_variable, csp.lcv, csp.mac)

    #Combine heuristique sur les variable et les valeurs avec MAC:
         #1/ mrv (Minimum remaining values)
    #MAC_mrv_lcv=csp.solution_search(k, csp.mrv, csp.lcv, csp.mac)
         #2/ dom/deg: 
    #MAC_domdeg_lcv=csp.solution_search(k, csp.dom_wdeg, csp.lcv, csp.mac)

    
    #m = csp.solution_search(k, csp.mrv, csp.lcv, csp.mac)


    end=time.time()

 
    k.display_all(m)
    print("nombre de valeurs testé: "+str(k.counter))
    print("temps d'execusion : "+str(end-begin) )
    print("Nombre de variables assignées: "+str(k.nassigns))
    """



    

if __name__ == '__main__':
    df = pd.read_csv('modules.csv')  # nom du fichier a lire
    k = Schedule(df)

    begin = time.time()


    time_list=[]
    count_list=[]
    ass_val_list=[]

    print('\n\n\n')

    """BT
    print('-'*30+"BackTracking model"+'-'*30)

# BackTracking search
  #Sans heuristique BT classique
    begin = time.time()
    BT_simple=csp.solution_search(k)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)
  #Avec heuristique
    #Heuristique sur les variables 
         #1/ mrv (Minimum remaining values)
    begin = time.time()
    k.nassigns=0
    BT_mrv=csp.solution_search(k, csp.mrv)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)
         #2/ dom/deg: 
    begin = time.time()
    k.nassigns=0
    BT_domdeg=csp.solution_search(k, csp.dom_wdeg)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)    

    #Heuristique sur les valeurs 


         #LCV least constraining values
    begin = time.time()
    k.nassigns=0
    BT_lcv=csp.solution_search(k, csp.first_unassigned_variable, csp.lcv)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

    #Combine heuristique sur les variable et les valeurs avec BT:
         #1/ mrv (Minimum remaining values)
    begin = time.time()
    k.nassigns=0
    BT_mrv_lcv=csp.solution_search(k, csp.mrv, csp.lcv)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

         #2/ dom/deg: 
    BT_domdeg_lcv=csp.solution_search(k, csp.dom_wdeg, csp.lcv)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

    Heuristiques=['simple','mrv','domdeg','lcv','mrv_lcv','domdeg_lcv']
    d = {'Heuristiques': Heuristiques ,'Temps d\'execusion': time_list,'Nbr de valeurs testés': count_list,'nbr de variable assignée': ass_val_list}
    df_temps_exec = pd.DataFrame(data=d)
    print(df_temps_exec )
    """


    """ FC
    print('-'*30+"Forward checking model"+'-'*30)
    #Forward checking search

    #Sans heuristique FC classique
    begin = time.time()
    k.nassigns=0
    FC_simple=csp.solution_search(k, csp.first_unassigned_variable, csp.unordered_domain_values, csp.forward_checking)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

    #Avec heuristique
    #Heuristique sur les variables 
         #1/ mrv (Minimum remaining values)
    begin = time.time()
    k.nassigns=0
    FC_mrv=csp.solution_search(k, csp.mrv, csp.unordered_domain_values, csp.forward_checking)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)
         #2/ dom/deg: 
    begin = time.time()
    k.nassigns=0

    FC_domdeg=csp.solution_search(k, csp.dom_wdeg, csp.unordered_domain_values, csp.forward_checking)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

    #Heuristique sur les valeurs 
         #LCV least constraining values
    begin = time.time()
    k.nassigns=0
    FC_lcv=csp.solution_search(k, csp.first_unassigned_variable, csp.lcv, csp.forward_checking)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

    #Combine heuristique sur les variable et les valeurs avec FC:
         #1/ mrv (Minimum remaining values)
    begin = time.time()
    k.nassigns=0
    FC_mrv_lcv=csp.solution_search(k, csp.mrv, csp.lcv, csp.forward_checking)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)
         #2/ dom/deg: 
    begin = time.time()
    k.nassigns=0
    FC_domdeg_lcv=csp.solution_search(k, csp.dom_wdeg, csp.lcv, csp.forward_checking)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

    Heuristiques=['simple','mrv','domdeg','lcv','mrv_lcv','domdeg_lcv']
    d2 = {'Heuristiques': Heuristiques ,'Temps d\'execusion': time_list,'Nbr de valeurs testés': count_list,'nbr de variable assignée': ass_val_list}
    df_temps_exec = pd.DataFrame(data=d2)
    print(df_temps_exec)
    """

    """ MAC
    print('-'*40+"MAC"+'-'*40)
#MAC search

  #Sans heuristique MAC classique
    begin = time.time()
    k.nassigns=0
    MAC_simple=csp.solution_search(k, csp.first_unassigned_variable, csp.unordered_domain_values, csp.mac)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

  #Avec heuristique

    #Heuristique sur les variables 
         #1/ mrv (Minimum remaining values)
    begin = time.time()
    k.nassigns=0
    MAC_mrv=csp.solution_search(k, csp.mrv, csp.unordered_domain_values, csp.mac)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

         #2/ dom/deg: 
    begin = time.time()
    k.nassigns=0
    MAC_domdeg=csp.solution_search(k, csp.dom_wdeg, csp.unordered_domain_values, csp.mac)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

    #Heuristique sur les valeurs 
         #LCV least constraining values
    begin = time.time()
    k.nassigns=0
    MAC_lcv=csp.solution_search(k, csp.first_unassigned_variable, csp.lcv, csp.mac)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

    #Combine heuristique sur les variable et les valeurs avec MAC:
         #1/ mrv (Minimum remaining values)
    begin = time.time()
    k.nassigns=0
    MAC_mrv_lcv=csp.solution_search(k, csp.mrv, csp.lcv, csp.mac)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)

         #2/ dom/deg:
    begin = time.time()
    k.nassigns=0 
    MAC_domdeg_lcv=csp.solution_search(k, csp.dom_wdeg, csp.lcv, csp.mac)
    end=time.time()
    time_list.append(end-begin)
    count_list.append(k.counter)
    ass_val_list.append(k.nassigns)  

    Heuristiques=['simple','mrv','domdeg','lcv','mrv_lcv','domdeg_lcv']
    d = {'Heuristiques': Heuristiques ,'Temps d\'execusion': time_list,'Nbr de valeurs testés': count_list,'nbr de variable assignée': ass_val_list}
    df_temps_exec = pd.DataFrame(data=d)
    print(df_temps_exec )
    """
    




 

#Forward checking search

  #Sans heuristique FC classique
    #FC_basic=csp.solution_search(k, csp.first_unassigned_variable, csp.unordered_domain_values, csp.forward_checking)

  #Avec heuristique
    #Heuristique sur les variables 
         #1/ mrv (Minimum remaining values)
    #FC_mrv=csp.solution_search(k, csp.mrv, csp.unordered_domain_values, csp.forward_checking)
         #2/ dom/deg: 
    #FC_domdeg=csp.solution_search(k, csp.dom_wdeg, csp.unordered_domain_values, csp.forward_checking)

    #Heuristique sur les valeurs 
         #LCV least constraining values
    #FC_lcv=csp.solution_search(k, csp.first_unassigned_variable, csp.lcv, csp.forward_checking)

    #Combine heuristique sur les variable et les valeurs avec FC:
         #1/ mrv (Minimum remaining values)
    #FC_mrv_lcv=csp.solution_search(k, csp.mrv, csp.lcv, csp.forward_checking)
         #2/ dom/deg: 
    #FC_domdeg_lcv=csp.solution_search(k, csp.dom_wdeg, csp.lcv, csp.forward_checking)



# BackTracking search
  #Sans heuristique BT classique
    BT_simple=csp.solution_search(k)

  #Avec heuristique
    #Heuristique sur les variables 
         #1/ mrv (Minimum remaining values)
    #BT_mrv=csp.solution_search(k, csp.mrv)

         #2/ dom/deg: 
    #BT_domdeg=csp.solution_search(k, csp.dom_wdeg)

    #Heuristique sur les valeurs 
         #LCV least constraining values
    #BT_lcv=csp.solution_search(k, csp.first_unassigned_variable, csp.lcv)

    #Combine heuristique sur les variable et les valeurs avec BT:
         #1/ mrv (Minimum remaining values)
    #BT_mrv_lcv=csp.solution_search(k, csp.mrv, csp.lcv)
         #2/ dom/deg: 
    #BT_domdeg_lcv=csp.solution_search(k, csp.dom_wdeg, csp.lcv)




#MAC search

  #Sans heuristique MAC classique
    #MAC_simple=csp.solution_search(k, csp.first_unassigned_variable, csp.unordered_domain_values, csp.mac)

  #Avec heuristique
    #Heuristique sur les variables 
         #1/ mrv (Minimum remaining values)
    #MAC_mrv=csp.solution_search(k, csp.mrv, csp.unordered_domain_values, csp.mac)
         #2/ dom/deg: 
    #MAC_domdeg=csp.solution_search(k, csp.dom_wdeg, csp.unordered_domain_values, csp.mac)

    #Heuristique sur les valeurs 
         #LCV least constraining values
    #MAC_lcv=csp.solution_search(k, csp.first_unassigned_variable, csp.lcv, csp.mac)

    #Combine heuristique sur les variable et les valeurs avec MAC:
         #1/ mrv (Minimum remaining values)
    #MAC_mrv_lcv=csp.solution_search(k, csp.mrv, csp.lcv, csp.mac)
         #2/ dom/deg: 
    #MAC_domdeg_lcv=csp.solution_search(k, csp.dom_wdeg, csp.lcv, csp.mac)

    
    #m = csp.solution_search(k, csp.mrv, csp.lcv, csp.mac)


    end=time.time()

 
    k.display_all(BT_simple)
   
    
    print("nombre de valeurs testé: "+str(k.counter))
    print("temps d'execusion : "+str(end-begin) )
    print("Nombre de variables assignées: "+str(k.nassigns))
    

print('\n\n\n')
