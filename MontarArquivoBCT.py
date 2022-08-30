#-------------------Importando Bibliotecas ---------------------------------------------------------
import numpy as np
import pandas as pd
from scipy.io import loadmat
import glob
import warnings
warnings.filterwarnings('ignore')
#---------------------------------------------------------------------------------------------------

#-----------------INÍCIO fronteiraDelft()-----------------------------------------------------------

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
        globals()["dado" + str(j)] = pd.read_csv(i,header = ent_header, index_col = 0)

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

#------------------------- INÍCIO da funcao estruturandoNovaEntrada --------------------------------
def estruturandoNovaEntrada(caminho,fronteira,fronteira1):
    ent_header = [0,1]
    DadoInicialS1 = openCSV(caminho, fronteira, fronteira1, ent_header)
    print("****entrada de arquivo novo***")
    ndias = len(DadoInicialS1.loc[:,DadoInicialS1.columns.get_level_values(0).isin(['1'])].columns)
    ncamadas = len(DadoInicialS1.loc[:,DadoInicialS1.columns.get_level_values(1).isin(['1'])].columns)
    nlinhas = np.arange(1, len(DadoInicialS1)+1,1)
    Ind1 = [fronteira1 + '{}'.format(x) for x in nlinhas]
    a = np.arange(1,ndias+1,1)
    A1 = np.concatenate([([i]*len(a)) for i in range(1,ncamadas+1)], axis=0)
    A1 = ["%02d" % n for n in A1]
    
    #IMPORTANTE: Como no ROMS a 1ª camada é o fundo e no Delft é o contrário, aqui acontece a inversão das camadas:
    A1 = A1[::-1]

    B1 = list(np.arange(1,len(a)+1))*ncamadas
    B1 = ["%05d" % n for n in B1]
    df_entrada1 = pd.DataFrame(np.array(DadoInicialS1), columns=pd.MultiIndex.from_tuples(zip(A1,B1)))
    df_entrada1.index = Ind1
    df_entrada1s = df_entrada1.stack(level=[0,1])
    df_entrada1u = df_entrada1s.unstack(level=[0,1])
    return df_entrada1u
#----------------------- FIM da funcao estruturandoNovaEntrada -------------------------------------

#-----------------------INÍCIO da função componentes_Alfa-------------------------------------------
def componentes_Alfa (fronteira, fronteira1, df_NovaEntradaU, df_NovaEntradaV, caminhoAlfa): #, caminhoDepth):
    #IMPORTANTE: No ROMS, as componentes U e V são referenciados ao Norte Verdadeiro e o Delft é referenciado ao Alpha, logo, aqui acontece o calculo das componentes em relação ao Alpha:
    ent_header = 0
    caminho = caminhoAlfa
    df_Alpha = openCSV(caminho, fronteira, fronteira1, ent_header)
    ncamadas = len(df_NovaEntradaU.loc[:,df_NovaEntradaU.columns.get_level_values(0).isin([fronteira1+str(1)])].columns)
    New_U1 = []
    New_V1 = []
    for k in range(31):
        U = np.array(df_NovaEntradaU.iloc[k])
        V = np.array(df_NovaEntradaV.iloc[k])
        Dir=np.mod(180+np.rad2deg(np.arctan2(U, V)),360)
        Mag = np.sqrt(U**2+V**2)
        Alpha = np.concatenate([([i]*ncamadas) for i in df_Alpha.Alpha], axis=0)
        New_U = (-1)*Mag*np.sin((np.pi/180)*(Dir+Alpha))
        New_V = (-1)*Mag*np.cos((np.pi/180)*(Dir+Alpha))
        New_U1.append(list(New_U))
        New_V1.append(list(New_V))

    nBeginEnd = len(df_NovaEntradaU.loc[:,df_NovaEntradaU.columns.get_level_values(1).isin(['01'])].columns)
    a = np.arange(1,nBeginEnd+1,1)
    Front = [fronteira1 + '{}'.format(x) for x in a]
    ndias = len(df_NovaEntradaU)
    A1 = np.concatenate([([i]*ncamadas) for i in Front], axis=0)
    B1 = list(np.arange(1,ncamadas+1))*nBeginEnd
    B1 = ["%02d" % n for n in B1]
    Ind = list(np.arange(1,ndias+1))
    df_U = pd.DataFrame(New_U1, columns=pd.MultiIndex.from_tuples(zip(A1,B1)))
    df_V = pd.DataFrame(New_V1, columns=pd.MultiIndex.from_tuples(zip(A1,B1)))
    df_U.index = df_NovaEntradaU.index
    df_V.index = df_NovaEntradaV.index

    df_Riemann = pd.DataFrame()
    #eta_m = df_Depth[]
    #depth_m = df_Depth[]
    if fronteira1 == 'East':
        df_Riemann = df_V#-eta_m*np.sqrt(9.81/depth_m)

    elif fronteira1 == 'South':
        df_Riemann =     df_U#-eta_m*np.sqrt(9.81/depth_m)

    elif fronteira1 == 'West':
        df_Riemann = df_V#+eta_m*np.sqrt(9.81/depth_m)
    else:
        print('Opção inválida. Revise a lista das fronteiras.')
       

    return df_U, df_V, df_Riemann

#------------------------ FIM da função componentes_Alfa -------------------------------------------

#----------------------- INÍCIO da funcao criarArquivoBCC ------------------------------------------
def criarArquivoBCC(fronteira, caminhoU, caminhoV, referenceTime, entradaTime, caminhoAlfa, caminhoSaida1, caminhoSaida2, caminhoSaida3):
    my_file = open(caminhoSaida3+'BCT_'+str(entradaTime)+'.txt', "w")
    for u in range(len(fronteira)):
        fronteira1 = fronteira[u]
        caminho = caminhoU
        df_NovaEntradaU = estruturandoNovaEntrada(caminho,fronteira,fronteira1)
        caminho = caminhoV
        df_NovaEntradaV = estruturandoNovaEntrada(caminho,fronteira,fronteira1)
        #IMPORTANTE: No ROMS, as componentes U e V são referenciados ao Norte Verdadeiro e o Delft é referenciado ao Alpha, logo, aqui acontece o calculo das componentes em relação ao Alpha:
        df_AlfaEntradaU, df_AlfaEntradaV, df_Riemann = componentes_Alfa(fronteira, fronteira1, df_NovaEntradaU, df_NovaEntradaV, caminhoAlfa)

        while True:
            try:
                perguntaInicial = int(input('Selecione a opção desejada:\n1 - Arquivo novo\n2 - Incremento de dados para um arquivo .BCC pré-existente\n>>'))
                if perguntaInicial == 1:
                    df_SerieCompletaU = df_AlfaEntradaU
                    df_SerieCompletaV = df_AlfaEntradaV
                    df_SerieCompletaU.to_csv(caminhoSaida1+fronteira1+'_compU_'+str(entradaTime)+'.csv')
                    df_SerieCompletaV.to_csv(caminhoSaida2+fronteira1+'_compV_'+str(entradaTime)+'.csv')
                    df_Riemann.to_csv(caminhoSaida3+fronteira1+'_Riemann_'+str(entradaTime)+'.csv')
                    print("*** Série histórica da fronteira "+ fronteira1+" nova criada com sucesso!***")
                    break
                elif perguntaInicial == 2:
                    ent_header = [0,1]
                    caminhoBCCu = str(input('\n Digitar o caminho que leva aos arquivos de SALINIDADE .CSV com a série temporal acumulada:\n>> '))
                    caminho = caminhoBCCu
                    df_DadoBCCu = openCSV(caminho, fronteira, fronteira1, ent_header)
                    caminhoBCCv = str(input('\n Digitar o caminho que leva aos arquivos de TEMPERATURA .CSV com a série temporal acumulada:\n>> '))
                    caminho = caminhoBCCv
                    df_DadoBCCv = openCSV(caminho, fronteira, fronteira1, ent_header)
                    ndias_novaentrada = len(df_AlfaEntradaU)
                    ndias_DadoBCC = len(df_DadoBCCu)
                    Newdias = list(np.arange(1, ndias_novaentrada+ndias_DadoBCC+1,1))
                    Newdias = ["%05d" % n for n in Newdias]
                    df_SerieCompletaU = pd.concat([df_DadoBCCu,df_AlfaEntradaU], axis =0)
                    df_SerieCompletaU.index = Newdias
                    df_SerieCompletaV = pd.concat([df_DadoBCCv,df_AlfaEntradaV], axis =0)
                    df_SerieCompletaV.index = Newdias
                    df_SerieCompletaU.to_csv(caminhoSaida1+fronteira1+'_compU_'+str(entradaTime)+'.csv')
                    df_SerieCompletaV.to_csv(caminhoSaida2+fronteira1+'_compV_'+str(entradaTime)+'.csv')
                    df_Riemann.to_csv(caminhoSaida3+fronteira1+'_Riemann_'+str(entradaTime)+'.csv')
                    print("*** Concluída a adição de nova série aos arquivos de séries acumuladas da fronteira "+fronteira1+"!***")
                    break
                else:
                    print('Opção inválida. Entrar novamente, apenas com número 1 ou 2.')
                    continue
            except ValueError:
                print('Opção inválida. Entrar novamente, apenas com número 1 ou 2.')
                continue

        nCelulas = len(df_Riemann.loc[:,df_Riemann.columns.get_level_values(1).isin(['01'])].columns)
        ncamadas = len(df_Riemann.loc[:,df_Riemann.columns.get_level_values(0).isin([fronteira1+str(1)])].columns)
        Celulas = np.arange(1,nCelulas+1)
        nfront = np.arange(1, (nCelulas)/2+1,1)
        ID_front = [fronteira1 + '{}'.format(int(x)) for x in nfront]                        
        odd_list = [x for x in Celulas if x % 2 != 0]
        Ind_odd = [fronteira1 + '{}'.format(x) for x in odd_list]
        even_list = [x for x in Celulas if x % 2 == 0]
        Ind_even = [fronteira1 + '{}'.format(x) for x in even_list]
        df_entrada_odd = df_Riemann[Ind_odd]
        df_entrada_even = df_Riemann[Ind_even]
        for k in range(len(ID_front)):
            my_file.write("table-name          'Boundary Section : "+str(k+1)+"'\n")
            my_file.write("contents            '3d-profile'\n")
            my_file.write("location            '"+fronteira1+str(k+1).zfill(2)+"'\n")
            my_file.write("time-function       'non-equidistant'\n")
            my_file.write("reference-time       "+str(referenceTime)+"\n")
            my_file.write("time-unit           'minutes'\n")
            my_file.write("interpolation       'linear'\n")
            my_file.write("parameter           'time' unit '[min]'\n")
            i=0
            for i in range(1, ncamadas+1):
                my_file.write("parameter           'Riemann         (R)  End A layer: "+str(i)+"' unit '[m/s]'\n")

            j=0
            for j in range(1, ncamadas+1):
                my_file.write("parameter           'Riemann         (R)  End B layer: "+str(j)+"' unit '[m/s]'\n")

            my_file.write("records-in-table     "+str(len(df_Riemann))+"\n")
            for m in range(len(df_SerieCompletaU)):
                u1 = df_entrada_odd[Ind_odd[k]].iloc[m]
                u2 = df_entrada_even[Ind_even[k]].iloc[m]
                u11 = u1.append(u2)
                u3 = ['%.7e' % x for x in u11]
                numbers_str = "   ".join([str(number) for number in u3])
                my_file.write("  " + numbers_str+"\n")



    my_file.close()
#----------------------------- FIM da funcao criarArquivoBCC ---------------------------------------

#----------------INÍCIO DO CÓDIGO PRINCIPAL---------------------------------------------------------
print('+ ================================================================================== +')
print('|                                                                                    |')
print('| Título: Montagem do arquivo .BCT para Condições de Contorno do DELFT3D-4           |')
print('|                                                                                    |')
print('| Autor: Oceanógrafo Marcelo Di Lello Jordão                                         |')
print('| Data: 03/08/2022                                                                   |')
print('| Contato: dilellocn@gmail.com                                                       |')
print('|                                                                                    |')
print('+ ================================================================================== +\n\n')

while True:
    try:
        opcao = int(input('Escolha a poção desejada [1 ou 2]:\n1 - Executar código de montagem de arquivo .BCT\n2 - Sair\n>>'))
        if opcao == 1:
            referenceTime = int(input('\n Entrar com a data [AAAAMMDD] de referência inicial do modelo (Ex.:20110101):\n>> '))
            entradaTime = int(input('\n Entrar com a data [AAAAMM] do arquivo que será incorporado na série acumulada  (Ex.:201101):\n>> '))
            caminhoU = str(input('\n Digitar o caminho que leva aos arquivos .CSV de COMPONENTE U que serão incorporada a série acumulada:\n>> '))
            caminhoV = str(input('\n Digitar o caminho que leva aos arquivos .CSV de COMPONENTE V que serão incorporada a série acumulada:\n>> '))
            caminhoAlfa = str(input('\n Digitar o caminho que leva aos arquivos .CSV dos angulos ALpha da Delft:\n>> '))
            caminhoSaida1 = str(input('\n Digitar o caminho de saída para o arquivo .CSV com a série histórica atualizada da COMPONENTE U:\n>> '))
            caminhoSaida2 = str(input('\n Digitar o caminho de saída para o arquivo .CSV com a série histórica atualizada da COMPONENTE V:\n>> '))
            caminhoSaida3 = str(input('\n Digitar o caminho de saída para o arquivo .BCT:\n>> '))
            fronteira = fronteiraDelft()
            criarArquivoBCC(fronteira, caminhoU, caminhoV, referenceTime, entradaTime, caminhoAlfa, caminhoSaida1, caminhoSaida2, caminhoSaida3)
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





