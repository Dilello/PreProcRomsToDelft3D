# -------------------Importando Bibliotecas ---------------------------------------------------------
import numpy as np
import pandas as pd
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
    #A1 = A1[::-1]
    
    B1 = list(np.arange(1,len(a)+1))*ncamadas
    B1 = ["%05d" % n for n in B1]
    df_entrada1 = pd.DataFrame(np.array(DadoInicialS1), columns=pd.MultiIndex.from_tuples(zip(A1,B1)))
    df_entrada1.index = Ind1
    df_entrada1s = df_entrada1.stack(level=[0,1])
    df_entrada1u = df_entrada1s.unstack(level=[0,1])
    return df_entrada1u
#----------------------- FIM da funcao estruturandoNovaEntrada -------------------------------------

#----------------------- INÍCIO da funcao criarArquivoBCC ------------------------------------------
def criarArquivoBCC(fronteira, caminhoS, caminhoT, referenceTime, entradaTime, caminhoSaida1, caminhoSaida2, caminhoSaida3):
    my_file = open(caminhoSaida3+'BCC_'+str(entradaTime)+'.txt', "w")
    for u in range(len(fronteira)):
        fronteira1 = fronteira[u]
        caminho = caminhoS
        df_NovaEntradaS = estruturandoNovaEntrada(caminho,fronteira,fronteira1)
        caminho = caminhoT
        df_NovaEntradaT = estruturandoNovaEntrada(caminho,fronteira,fronteira1)
        while True:
            try:
                perguntaInicial = int(input('Selecione a opção desejada:\n1 - Arquivo novo\n2 - Incremento de dados para um arquivo .BCC pré-existente\n>>'))
                if perguntaInicial == 1:
                    df_SerieCompletaS = df_NovaEntradaS
                    df_SerieCompletaT = df_NovaEntradaT
                    df_TimeStep = pd.DataFrame()
                    TimeStep = []
                    for i in range(len(df_SerieCompletaS)):
                        x1 = i*1440
                        TimeStep.append(x1)

                    df_TimeStep['Step'] = TimeStep
                    df_SerieCompletaS.to_csv(caminhoSaida1+fronteira1+'_Salt_'+str(entradaTime)+'.csv')
                    df_SerieCompletaT.to_csv(caminhoSaida2+fronteira1+'_Temp_'+str(entradaTime)+'.csv')
                    print("*** Série histórica da fronteira "+ fronteira1+" nova criada com sucesso!***")
                    break
                elif perguntaInicial == 2:
                    ent_header = [0,1]
                    caminhoBCCs = str(input('\n Digitar o caminho que leva aos arquivos de SALINIDADE .CSV com a série temporal acumulada:\n>> '))
                    caminho = caminhoBCCs
                    df_DadoBCCs = openCSV(caminho, fronteira, fronteira1, ent_header)
                    caminhoBCCt = str(input('\n Digitar o caminho que leva aos arquivos de TEMPERATURA .CSV com a série temporal acumulada:\n>> '))
                    caminho = caminhoBCCt
                    df_DadoBCCt = openCSV(caminho, fronteira, fronteira1, ent_header)
                    ndias_novaentrada = len(df_NovaEntradaS)
                    ndias_DadoBCC = len(df_DadoBCCs)
                    Newdias = list(np.arange(1, ndias_novaentrada+ndias_DadoBCC+1,1))
                    Newdias = ["%05d" % n for n in Newdias]
                    df_SerieCompletaS = pd.concat([df_DadoBCCs,df_NovaEntradaS], axis =0)
                    df_SerieCompletaS.index = Newdias
                    df_TimeStep = pd.DataFrame()
                    TimeStep = []
                    for i in range(len(df_SerieCompletaS)):
                        x1 = i*1440
                        TimeStep.append(x1)
                        
                    df_TimeStep['Step'] = TimeStep
                    df_SerieCompletaT = pd.concat([df_DadoBCCt,df_NovaEntradaT], axis =0)
                    df_SerieCompletaT.index = Newdias
                    df_SerieCompletaS.to_csv(caminhoSaida1+fronteira1+'_Salt_'+str(entradaTime)+'.csv')
                    df_SerieCompletaT.to_csv(caminhoSaida2+fronteira1+'_Temp_'+str(entradaTime)+'.csv')
                    print("*** Concluída a adição de nova série aos arquivos de séries acumuladas da fronteira "+fronteira1+"!***")
                    break
                else:
                    print('Opção inválida. Entrar novamente, apenas com número 1 ou 2.')
                    continue
            except ValueError:
                print('Opção inválida. Entrar novamente, apenas com número 1 ou 2.')
                continue

        nCelulas = len(df_SerieCompletaS.loc[:,df_SerieCompletaS.columns.get_level_values(1).isin(['01'])].columns)
        ncamadas = len(df_SerieCompletaS.loc[:,df_SerieCompletaS.columns.get_level_values(0).isin([fronteira1+str(1)])].columns)
        Celulas = np.arange(1,nCelulas+1)
        nfront = np.arange(1, (nCelulas)/2+1,1)
        ID_front = [fronteira1 + '{}'.format(int(x)) for x in nfront]                        
        odd_list = [x for x in Celulas if x % 2 != 0]
        Ind_odd = [fronteira1 + '{}'.format(x) for x in odd_list]
        even_list = [x for x in Celulas if x % 2 == 0]
        Ind_even = [fronteira1 + '{}'.format(x) for x in even_list]
        df_entrada_oddS = df_SerieCompletaS[Ind_odd]
        df_entrada_evenS = df_SerieCompletaS[Ind_even]
        df_entrada_oddT = df_SerieCompletaT[Ind_odd]
        df_entrada_evenT = df_SerieCompletaT[Ind_even]
        if fronteira1 == 'South':
            ff = 1
        elif fronteira1 == 'West':
            ff = 73
        elif fronteira1 == 'East':
            ff = 84
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
                my_file.write("parameter           'Salinity             end A layer "+str(i)+"' unit '[ppt]'\n")

            j=0
            for j in range(1, ncamadas+1):
                my_file.write("parameter           'Salinity             end B layer "+str(j)+"' unit '[ppt]'\n")

            my_file.write("records-in-table     "+str(len(df_SerieCompletaS))+"\n")
            for m in range(len(df_SerieCompletaS)):
                s0 = df_TimeStep.iloc[m]
                s1 = df_entrada_oddS[Ind_odd[k]].iloc[m]
                s10 = s0.append(s1)
                s2 = df_entrada_evenS[Ind_even[k]].iloc[m]
                s11 = s10.append(s2)
                s3 = ['%.7e' % x for x in s11]
                numbers_str = "   ".join([str(number) for number in s3])
                my_file.write("  " + numbers_str+"\n")

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
                my_file.write("parameter           'Temperature          end A layer "+str(i)+"' unit '[C]'\n")

            j=0
            for j in range(1, ncamadas+1):
                my_file.write("parameter           'Temperature          end B layer "+str(j)+"' unit '[C]'\n")

            my_file.write("records-in-table     "+str(len(df_SerieCompletaS))+"\n")
            for n in range(len(df_SerieCompletaS)):
                t0 = df_TimeStep.iloc[n]
                t1 = df_entrada_oddT[Ind_odd[k]].iloc[n]
                t2= df_entrada_evenT[Ind_even[k]].iloc[n]
                t10 = t0.append(t1)
                t11 = t10.append(t2)
                t3 = ['%.7e' % x for x in t11]
                numbers_str = "   ".join([str(number) for number in t3])
                my_file.write("  " + numbers_str+"\n")



    my_file.close()
#----------------------------- FIM da funcao criarArquivoBCC ---------------------------------------

#----------------INÍCIO DO CÓDIGO PRINCIPAL---------------------------------------------------------
print('+ ================================================================================== +')
print('|                                                                                    |')
print('| Título: Montagem do arquivo .BCC para Condições de Contorno do DELFT3D-4           |')
print('|                                                                                    |')
print('| Autor: Oceanógrafo Marcelo Di Lello Jordão                                         |')
print('| Data: 03/08/2022                                                                   |')
print('| Contato: dilellocn@gmail.com                                                       |')
print('|                                                                                    |')
print('+ ================================================================================== +\n\n')

while True:
    try:
        opcao = int(input('Escolha a poção desejada [1 ou 2]:\n1 - Executar código montagem do arquivo BCC\n2 - Sair\n>>'))
        if opcao == 1:
            referenceTime = int(input('\n Entrar com a data [AAAAMMDD] de referência inicial do modelo (Ex.:20110101):\n>> '))
            entradaTime = int(input('\n Entrar com a data [AAAAMM] do arquivo que será incorporado na série acumulada  (Ex.:201101):\n>> '))
            caminhoS = str(input('\n Digitar o caminho que leva aos arquivos .CSV de SALINIDADE que serão incorporada a série acumulada:\n>> '))
            caminhoT = str(input('\n Digitar o caminho que leva aos arquivos .CSV de TEMPERATURA que serão incorporada a série acumulada:\n>> '))
            caminhoSaida1 = str(input('\n Digitar o caminho de saída para o arquivo .CSV com a série histórica atualizada da SALINIDADE:\n>> '))
            caminhoSaida2 = str(input('\n Digitar o caminho de saída para o arquivo .CSV com a série histórica atualizada da TEMPERATURA:\n>> '))
            caminhoSaida3 = str(input('\n Digitar o caminho de saída para o arquivo .BCC:\n>> '))
            fronteira = fronteiraDelft()
            criarArquivoBCC(fronteira, caminhoS, caminhoT, referenceTime, entradaTime, caminhoSaida1, caminhoSaida2, caminhoSaida3)
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



