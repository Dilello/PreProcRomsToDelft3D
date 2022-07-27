import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy import interpolate
import matplotlib.pyplot as plt

 

mat = loadmat('Documents\\Projetos\\RedeRioDoce\\MODELO\\ROMS\\Contornos_ROMS_e_Delft\\Salt_Jan_2018.mat')
posicao = np.loadtxt('Documents\\Projetos\\RedeRioDoce\\MODELO\\ROMS\\teste_v4.txt')
mdata = mat['uu']
index = pd.MultiIndex.from_product([range(s)for s in mdata.shape])
df = pd.DataFrame({'mdata': mdata.flatten()}, index=index)['mdata']
df = df.unstack(level=[0]).swaplevel().sort_index()
df.index.names = ['CamadaSigma', 'dia']
df1 = df.T
df1['Long'] = posicao[:,1]
df1['Lat'] = posicao[:,2]

#df1.loc[:,df1.columns.get_level_values(1).isin([0])] # df1.loc[:,df1.columns.get_level_values(Fixa a Camada = 1).isin([Valor da Camada])]
#df1.loc[:,df1.columns.get_level_values(0).isin([0])] # df1.loc[:,df1.columns.get_level_values(Fixa o Dia = 0).isin([Valor do Dia])]

#arrays constituting the 3D grid
long_roms = df1.Long
lat_roms = df1.Lat
S = df1.loc[:,df1.columns.get_level_values(1).isin([0])]
S_roms = S.loc[:,0]
# evaluate the function on the points of the grid
# points = the regular grid, #values =the data on the regular grid
# point = the point that we want to evaluate in the 3D grid
f = interpolate.interp2d(long_roms, lat_roms, S_roms)
