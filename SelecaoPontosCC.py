## -------------------Importando Bibliotecas ---------------------------------------------------------

import numpy as np
from scipy.io import loadmat
import pandas as pd
import math
import glob
import warnings
warnings.filterwarnings('ignore')

#-------------------FIM da importação --------------------------------------------------------------

#-----------------INÍCIO fronteiraDelft ------------------------------------------------------------

def fronteiraDelft():
    fronteira  = []
    while True:
        try:
            pergunta1 = str(input('\n Entrar com o nome da fronteira do Delft (Exemplo: East, South, West):\n>> '))
            fronteira.append(pergunta1)
            print(fronteira)
            pergunta2 = str(input('Deseja inserir mais nomes [S/N]:\n>>'))
            if pergunta2 in 'Ss':
                continue
            elif pergunta2 in 'Nn':
                break
            else:
                continue
        except ValueError:
            print('Opção inválida. Utilizar apenas nomes. Tente novamente...')
            continue

    return fronteira

#-----------------FIM fronteiraDelft()--------------------------------------------------------------

#-----------------INÍCIO função openCSV-------------------------------------------------------------

def openCSV(caminho, fronteira, fronteira1, ent_header):

    j = 0
    for i in glob.glob(caminho+'*.csv', recursive = True):
        j += 1
        globals()["dado" + str(j)] = pd.read_csv(i,sep = ';',header = ent_header, index_col = 0)

    while True:
        try:
            if fronteira1 == fronteira[0]:
                ArqSaida = dado1
                break
            elif fronteira1 == fronteira[1]:
                ArqSaida = dado2
                break
            elif fronteira1 == fronteira[2]:
                ArqSaida = dado3
                break
            elif fronteira1 == fronteira[3]:
                ArqSaida = dado4
                break
            else:
                print('Opção inválida. Revise a lista das fronteiras.')
                continue
        except ValueError:
            print('Valor inválido. Entrar apenas com valores numéricos.')
            continue

    return ArqSaida
#----------------FIM da função openCSV -------------------------------------------------------------

#----------------INÍCIO função distEuclediana-------------------------------------------------------

def distEuclediana (Ind, pontos1, pontos2, fronteira1):
    dist = []
    listaLat1 = []
    listaLong1 = []
    listaLong2 = []
    listaLat2 = []
    listatrecho = []

    for j in range(len(pontos2)):
        for i in range(len(pontos1)):
            xa = pontos1[i][0]
            xb = pontos2[j][0]
            ya = pontos1[i][1]
            yb = pontos2[j][1]
            Ind1 = Ind[j]
            # Formula da distancia Euclediana
            distance = math.sqrt(((xa-xb)**2) + ((ya-yb)**2))
            dist.append(distance)
            listaLong1.append(xa)
            listaLong2.append(xb)
            listaLat1.append(ya)
            listaLat2.append(yb)
            listatrecho.append(Ind1)

    distance_list = pd.DataFrame(
        {'dist': dist,
         'Long1': listaLong1,
         'Lat1': listaLat1,
         'Long2': listaLong2,
         'Lat2':listaLat2
        })

    distance_list.index = listatrecho

    df_trecho1 = pd.DataFrame()
    for k in Ind:
        df_trecho = distance_list.loc[k][distance_list.loc[k].dist == distance_list.loc[k].dist.min()]
        df_trecho1 = df_trecho1.append(df_trecho)

    return df_trecho1

#-----------------FIM função distEuclediana --------------------------------------------------------

#----------------INÍCIO função selectPoint ---------------------------------------------------------

def selectPoint(caminhoDELFT, caminhoCamadaROMS, arqCamadaROMS, caminhoLatLongROMS, caminhoSaida1, fronteira1):
    print('***Seleção dos pontos do ROMS para CC do DELFT***\n')        
    caminho = caminhoDELFT
    ent_header = 0
    delft_input = openCSV(caminho, fronteira, fronteira1, ent_header)
    roms_input1 = pd.read_csv(caminhoCamadaROMS+arqCamadaROMS, header = [0,1], index_col = 0)
    LongLatRoms = np.loadtxt(caminhoLatLongROMS)
    roms_input1['Long'] = LongLatRoms[:,1]
    roms_input1['Lat'] = LongLatRoms[:,2]
    pontosroms = roms_input1[['Long','Lat']]
    pontosroms1 = np.array(pontosroms)
    pontosdelft = delft_input[['Long','Lat','M','N']]
    pontosdelft.reset_index(inplace=True)
    pontosdelft1 = pontosdelft.iloc[np.arange(pontosdelft.shape[0]) % 2 != 0]
    pontosdelft2 = pd.DataFrame(np.repeat(pontosdelft1.values, 2, axis=0), columns=pontosdelft1.columns)
    pontosdelft3 = pontosdelft2[:len(pontosdelft2)-1]
    pontosdelft3.loc[-1] = pontosdelft.iloc[0]
    pontosdelft3.index = pontosdelft3.index + 1 
    pontosdelft3.sort_index(inplace=True)
    pontosdelft4 = pontosdelft3[['Long','Lat','M','N']]
    pontosdelft5 = np.array(pontosdelft4[['Long','Lat']])
    a = np.arange(1,len(pontosdelft5)+1,1)
    Ind = [fronteira1 + '{}'.format(x) for x in a]
    pontos1 = pontosroms1
    pontos2 = pontosdelft5
    df_trecho2 = distEuclediana (Ind, pontos1, pontos2, fronteira1)
    select_roms1 = pd.DataFrame()
    for m in Ind:
        select_roms = roms_input1.loc[(roms_input1['Long'] == df_trecho2['Long1'].loc[m]) & (roms_input1['Lat'] == df_trecho2['Lat1'].loc[m])]
        select_roms1 = select_roms1.append(select_roms)

    select_roms1.index = Ind
    select_roms2 = select_roms1.drop(['Long', 'Lat'], axis=1)
    select_roms2.to_csv(caminhoSaida1+fronteira1+'_'+arqCamadaROMS)
    print('Arquivos Salvos com Sucesso!')
    pontosdelft4.index = Ind
    df_trecho2['M'] = pontosdelft4.M
    df_trecho2['N'] = pontosdelft4.N
    return df_trecho2
#----------------FIM da função selectPoint ---------------------------------------------------------

#----------------INÍCIO da função LongLatMNAlpha----------------------------------------------------

def LongLatMNAlpha (caminhoalpha, resultado1, caminhoSaida2, fronteira1):

    alpha_input = pd.read_csv(caminhoalpha, header = 0, index_col = 0)
    pontosalpha = np.array(alpha_input[['LONGITUDE','LATITUDE']])
    a = np.arange(1,len(resultado1)+1,1)
    Ind = [fronteira1 + '{}'.format(x) for x in a]
    pontos1 = pontosalpha
    pontos2 = np.array(resultado1[['Long1','Lat2']])
    df_trecho3 = distEuclediana (Ind, pontos1, pontos2, fronteira1)
    select_alpha1 = pd.DataFrame()
    for n in Ind:
        select_alpha = alpha_input.loc[(alpha_input['LONGITUDE'] == df_trecho3['Long1'].loc[n]) & (alpha_input['LATITUDE'] == df_trecho3['Lat1'].loc[n])]
        select_alpha1 = select_alpha1.append(select_alpha)

    select_alpha1.index = Ind
    df_trecho3['Alpha'] = select_alpha1.ALFAS
    df_trecho3.to_csv(caminhoSaida2+fronteira1+'LongLatMNAlpha.csv')
    return df_trecho3
#----------------FIM da função LongLatMNAlpha ---------------------------------------------------------

#----------------INÍCIO DO CÓDIGO PRINCIPAL---------------------------------------------------------
print('+ ================================================================================== +')
print('|                                                                                    |')
print('| Título: Seleção dos pontos do ROMS para Condições de Contorno do DELFT3D-4         |')
print('|                                                                                    |')
print('| Autor: Oceanógrafo Marcelo Di Lello Jordão                                         |')
print('| Data: 03/08/2022                                                                   |')
print('| Contato: dilellocn@gmail.com                                                       |')
print('|                                                                                    |')
print('+ ================================================================================== +\n\n')

roms_input = pd.DataFrame()
delft_input = pd.DataFrame()
resultado1 = pd.DataFrame()
resultado2 = pd.DataFrame()
fronteira = fronteiraDelft()
caminhoDELFT = str(input('\n Digitar o caminho que leva aos arquivos .CSV de Lat e Log do Delft:\n>> '))
caminhoLatLongROMS = input('\n Digitar o caminho e nome do arquivo com a extensão .TXT referente a lat e long dos pontos do ROMS:\n>> ')
while True:
    try:
        opcao = int(input('Escolha a poção desejada [1 ou 2]:\n1 - Executar código de seleção de pontos do ROMS\n2 - Sair\n>>'))
        if opcao == 1:
            caminhoCamadaROMS = str(input('\n Digitar o caminho que leva ao arquivos do ROMS interpolados na camadas do Delft:\n>> '))
            arqCamadaROMS = str(input('Digitar nome arquivo do ROMS interpolados na camadas do Delft com a extensão .CSV:\n>> '))
            caminhoSaida1 = input('\n Entrar com o caminho do diretório de saída de pontos selecionados do ROMS:\n>> ')
            for i in range(len(fronteira)):
                fronteira1 = fronteira[i]
                resultado1 = selectPoint(caminhoDELFT, caminhoCamadaROMS, arqCamadaROMS, caminhoLatLongROMS, caminhoSaida1, fronteira1)
                print ('Arquivos da fronteria'+fronteira1+'gerados com sucesso!')
                while True:
                    try:
                        opcao1 = int(input('Escolha a poção desejada [1 ou 2]:\n1 - Executar criação de arquivo LongLatMNAlpha\n2 - Continua\n>>'))
                        if opcao1 == 1:
                            caminhoalpha = input('\n Digitar o caminho e nome do arquivo com a extensão .CSV referente aos Alphas dos pontos do Delft:\n>> ')
                            caminhoSaida2 = input('\n Entrar com o caminho do diretório de saída:\n>> ')
                            resultado2 = LongLatMNAlpha (caminhoalpha, resultado1, caminhoSaida2, fronteira1)
                            print ('Arquivos LongLatMNAlpha gerados com sucesso!')
                            break
                        else:
                            break
                    except ValueError:
                        print('Opção inválida. Entrar novamente, apenas com número 1 ou 2.')
                        continue

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
