#-------------------Importando Bibliotecas ---------------------------------------------------------

import numpy as np
from scipy.io import loadmat
import pandas as pd
import math
import glob
from scipy import interpolate
from scipy.interpolate import griddata
import warnings
warnings.filterwarnings('ignore')

#-------------------FIM da importação --------------------------------------------------------------

#----------------- INÍCIO função listaVar() --------------------------------------------------------

def listaVar():
    ano1 = ['2018','2019','2020','2021','2022','2023']
    mes1 = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']

    listaComU = []
    listaComV = []
    listaProf = []
    listaSalt = []
    listaTemp = []
    for i in mes1:
        arq1 = str('componenteU_' + '{}_'.format(i))
        arq2 = str('componenteV_' + '{}_'.format(i))
        arq3 = str('profundidade_' + '{}_'.format(i))
        arq4 = str('Salt_' + '{}_'.format(i))
        arq5 = str('Temp_' + '{}_'.format(i))
        for j in ano1:
            arq6 = str(arq1 + '{}'.format(j))
            arq7 = str(arq2 + '{}'.format(j))
            arq8 = str(arq3 + '{}'.format(j))
            arq9 = str(arq4 + '{}'.format(j))
            arq10 = str(arq5 + '{}'.format(j))
            listaComU.append(arq6)
            listaComV.append(arq7)
            listaProf.append(arq8)
            listaSalt.append(arq9)
            listaTemp.append(arq10)

    listaVariaveis = pd.DataFrame({'ComU': listaComU, 'ComV': listaComV, 'Prof': listaProf, 'Salt': listaSalt, 'Temp': listaTemp})

    return listaVariaveis

#----------------- FIM função listaVar() -----------------------------------------------------------

#----------------- INÍCIO função openROMS ----------------------------------------------------------
def openROMS(caminhoROMS, arquivo, listas):

    print('***Entrada dos parâmetros dos pontos do ROMS na fronteira***\n')

    dadoBrutoRoms = loadmat(caminhoROMS+arquivo+'.mat')

    
    if arquivo in np.array(listas.ComU):
        variavelEntrada = 'uu'
    elif arquivo in np.array(listas.ComV):
        variavelEntrada = 'vv'
    elif arquivo in np.array(listas.Prof):
        variavelEntrada = 'prof_final'
    elif arquivo in np.array(listas.Salt):
        variavelEntrada = 'salt_final'
    elif arquivo in np.array(listas.Temp):
        variavelEntrada = 'temp_final'
    else:
        print('Nome de arquivo inválido. Tente novamente...')


    #Estruturando um DataFrame dos Pontos de fronteira do ROMS
    mdata = dadoBrutoRoms[variavelEntrada]
    index = pd.MultiIndex.from_product([range(s) for s in mdata.shape])
    df = pd.DataFrame({'mdata': mdata.flatten()}, index=index)['mdata']
    df = df.unstack(level=[0]).swaplevel().sort_index()
    df.index.names = ['Dia', 'Camada']
    df.columns.names = ['Ponto']
    RomsBruto = df.T

    return RomsBruto


#------------------FIM da função openROMS-----------------------------------------------------------

#-----------------INÍCIO da função InterpVertical --------------------------------------------------
def InterpVertical(prof_input, roms_input, caminhoCamadas , arquivoMat, caminhoSaida1):

    delftprof = np.loadtxt(caminhoCamadas)
    dadoSaida = []
    ndias = len(prof_input.loc[:,prof_input.columns.get_level_values(1).isin([0])].T)
    ncamadas = len(prof_input.loc[:,prof_input.columns.get_level_values(0).isin([0])].T)
    for i in range(0, ndias):
        FrontCC1 = prof_input.loc[:,prof_input.columns.get_level_values(0).isin([i])]
        FrontCC2 = roms_input.loc[:,roms_input.columns.get_level_values(0).isin([i])]
        roms_bat_roms = FrontCC1.T
        roms_salt_roms = FrontCC2.T
        for j in range(0,len(FrontCC1)):
            x0 = np.array(roms_bat_roms[j])
            y0 =  np.array(roms_salt_roms[j])
            espessuraCamada = x0[0]-x0[1]
            minimo = min(roms_bat_roms[j])
            entradaprof = delftprof*(minimo+(espessuraCamada/2.))
            f1 = interpolate.interp1d(x0, y0,kind='linear',fill_value = 'extrapolate')
            #f2 = interpolate.interp1d(x0, y0,kind='cubic')
            #f3 = interpolate.interp1d(x0, y0,kind='quadratic')
            Saltsaida1 = f1(entradaprof)
            #Saltsaida2 = f2(entradaprof)
            #Saltsaida3 = f3(entradaprof)
            Saida = list(Saltsaida1)
            dadoSaida.append(Saida)

    a = np.arange(1,len(FrontCC1)+1,1)
    A = np.concatenate([([i]*len(a)) for i in range(1,ndias+1)], axis=0)
    #Ind = [fronteira1 + '{}'.format(x) for x in a]
    B = list(np.arange(1,len(a)+1))*ndias
    C = np.array(dadoSaida)
    C1 = C.T
    df_Interpolado = pd.DataFrame(C1, columns=pd.MultiIndex.from_tuples(zip(A,B)))
    df_Interpolado.index = np.arange(1,len(delftprof)+1)
    df_Interpolado.index.names = ['Camada']
    df_Interpolado.columns.names = ['Dia','Ponto']
    df1 = df_Interpolado.stack(level=[0,1])
    df_Interpolado1 = df1.unstack(level=[0,1])
    df_Interpolado1.to_csv(caminhoSaida1+arquivoMat+'_'+str(len(delftprof))+'.csv')
    return df_Interpolado1
#----------------- FIM da função InterpVertical ----------------------------------------------------

#----------------INÍCIO DO CÓDIGO PRINCIPAL---------------------------------------------------------
print('+ ================================================================================== +')
print('|                                                                                    |')
print('| Título: Interpolação das camadas dos dados do ROMS para as camadas do DELFT3D-4    |')
print('|                                                                                    |')
print('| Autor: Oceanógrafo Marcelo Di Lello Jordão                                         |')
print('| Data: 03/08/2022                                                                   |')
print('| Contato: dilellocn@gmail.com                                                       |')
print('|                                                                                    |')
print('+ ================================================================================== +\n\n')

print('IMPORTANTE: Antes de começar crie um arquivo .TXT com as proporções das camadas de interesse.\n')
print('Exemplo de 10 camadas: 1.0  0.95  0.90  0.80  0.70  0.50  0.30  0.20  0.10  0.05\n')

roms_input = pd.DataFrame()
prof_input = pd.DataFrame()
delft_input = pd.DataFrame()
resultado = pd.DataFrame()
caminhoROMS = str(input('\n Digitar o caminho que leva ao arquivos .MAT do ROMS:\n>> '))
mes = input('\n Entrar com o mês de interesse [jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez]:\n>> ')
ano = int(input('\n Entrar com o ano de interesse (Ex.: 2022):\n>> '))
arquivoprof = 'profundidade'+'_'+mes+'_'+str(ano)
while True:
    try:
        opcao = int(input('Escolha a poção desejada [1 ou 2]:\n1 - Executar código\n2 - Sair\n>>'))
        if opcao == 1:
            arquivoMat = str(input('Digitar nome arquivo SEM a extensão .MAT do parâmetro de interesse:\n>> '))
            caminhoCamadas = str(input('\n Digitar o caminho com nome arquivo .TXT referente a proporção das camadas do Delft:\n>> '))
            listas = listaVar()
            caminhoSaida1 = input('\n Entrar com o caminho do diretório de saída de dados processados:\n>> ')
            arquivo = arquivoprof
            prof_input = openROMS(caminhoROMS, arquivo, listas)
            arquivo = arquivoMat
            roms_input = openROMS(caminhoROMS, arquivo, listas)
            resultado = InterpVertical(prof_input, roms_input, caminhoCamadas , arquivoMat, caminhoSaida1)
            print ('Arquivos gerados com sucesso!')
            continue
        elif opcao == 2:
            break
        else:
            print('Opção inválida. Entrar novamente, apenas com número 1 ou 2.')
            continue
    except ValueError:
        print('Opção inválida. Entrar novamente, apenas com número 1 ou 2.')
        continue
print('Programa finalizado!')

#----------------FIM DO CÓDIGO PRINCIPAL------------------------------------------------------------ 
