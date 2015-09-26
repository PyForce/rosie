# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 22:43:58 2015

@author: Toni
"""

############### NODE ################
class Node:    
    def __init__(self, pos=()):    
        self.pos=pos
        
    def __lt__(self, other):
        return True

#################################################
#               ADJACENCY MATRIX                #
#################################################

class AdjacencyMatrix :
    def __init__(self, V, E):
        self.index={}
        i=0
        for v in V :
            self.index [v]=i
            i += 1
        self.matrix=[]
        for i in range(len(V)):
            self.matrix. append([False] * len(V))
        for(u,v) in E: 
            self.matrix [self.index [u]][self.index [v]]=True
    
    def __contains__(self, item):
        (u, v)=item
        return self.matrix [self.index [u]][self.index [v]]
    
    def __setitem__(self, item, value):
        (u,v)=item
        self.matrix [self.index [u]][self.index [v]]=value
    
    def __getitem__(self, item):
        (u,v)=item
        return self.matrix [self.index [u]][self.index [v]]

class AdjacencyMatrixGraph:
    def __init__(self, V =[], E=[], L=[], directed =True):
        self.directed=directed
        self.V=V
        self.L=L
        if directed : 
            self.E=AdjacencyMatrix(V, E)
        else:
            self.E=AdjacencyMatrix(V, E+[(v,u) for(u,v) in E])
    
    def succs(self, u):
        return [v for v in self.V if self.E[u, v]]
    
    def preds(self, v):
        return [u for u in self.V if self.E[u, v]]
    
    def show(self):
        print(' %-12s| %-35s| %-29s' % ('Vertex', 'Succs', 'Preds'))
        print('-'*13+'+'+'-'*36+'+'+'-'*30)
        for v in self.V:
            aux_succ=''
            for w in self.succs(v): 
                aux_succ+=str(w)+' '
            aux_pred=''
            for u in self.preds(v):
                aux_pred+=str(u)+' '
            print(' %-12s| %-35s| %-29s' % (v, aux_succ, aux_pred))
    
    #---- position of TAG ----
    def pos_of(self,name):
        if type(name) is dict:
            try:
                n=name['place']
                for l in self.L:
                    if l[0].count(n):
                        try:
                            return l[1][name['pos']]
                        except:
                            return l[1][None][0]
            except: pass
        elif type(name) is str:
            for l in self.L:
                if l[0].count(name):
                    return l[1][None][0]
        elif type(name) is tuple:
            for v in self.V:
                if v.pos==name:
                    return v
        return None
