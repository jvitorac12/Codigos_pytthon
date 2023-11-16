### Código Backup Videos Parte 1 ####
### Movendo  vídeos das câmeras 7 e 8 para os discos de armazenamento

import shutil
import os
from datetime import datetime
from tqdm import tqdm
import funcoes_move_videos as fmv

# Trabalhando com datas
hoje = datetime.today()
mes_atual = hoje.month
ano_atual = hoje.year
dia_atual = hoje.day

# Diretório de origem dos vídeos
origem = r"D:\1005"

# Dicionário com as unidades de discos e seus tamanhos totais
tamanho_total_unidade_de_disco = fmv.verifica_espaco_total()

# Dicionário com as unidades de discos e os espaços livres em disco
espaco_diponivel_unidade_de_disco = fmv.verifica_espaco_disponivel()

# Meses do ano
meses_do_ano = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

fmv.zera_parametros_configuracao()

# Verificando se todas as pastas referente aos dias de ano atual existem no diretório de destino. Caso não existam, quer dize que é provavel que exista arquivos referentes as cameras 7 e 8 nestas pastas.
pastas = []

# O erro em questão acontece se eu descomentar o trecho abaixo. o codigo parece que nao le a lista de pastas ou a ignora e ja pula direto para a o envio de mensagem pelo whatsapp.

#for dir_pasta in os.listdir(origem):
#  pasta_procurada = os.path.join(str(ano_atual)+'-'+str(mes_atual))
#     if os.path.isdir(os.path.join(origem, dir_pasta)) and dir_pasta.startswith(str(pasta_procurada)):
#         dir_pasta_origem = os.path.join(origem, dir_pasta)
#         pastas.append(dir_pasta) 

# print(pastas)

# Acessando pasta de origem dos vídeos.
# for pasta_referencia in pastas:
#  continua o restante do codigo com ifs e fors

pasta_referencia = os.path.join(origem, str(hoje.strftime("%Y-%m-%d")))

if os.path.exists(pasta_referencia):
        cameras_selecionadas = [7,8] 
        arquivos_correspondentes_diretorio = []

        #Listando todos os arquivos da pasta de referencia.
        for nome_arquivo in os.listdir(pasta_referencia):  
            # Selecionando todos os arquivos que forem das cam 7 e 8.
            if nome_arquivo[0] in str(cameras_selecionadas):
                diretorio_arquivo = os.path.join(pasta_referencia, nome_arquivo)
                arquivos_correspondentes_diretorio.append(diretorio_arquivo)

        # Calculando o tamanho dos arquivos contidos na lista arquivos_correspondentes.
        tamanho_arquivos = 0

        for arquivo in arquivos_correspondentes_diretorio:
            if os.path.isfile(arquivo):
                tamanho_arquivo_unico = os.path.getsize(arquivo)
                tamanho_arquivos += tamanho_arquivo_unico

        # Verificando se há  espaço suficiente para mover os arquivos para o diretorio de destino.
        # Por hierarquia, a unidade F: tem prioridade. Quando estiver cheia, os backups passarão para a unidade E: e assim por diante segundo a hierarquia.
        # Caso seja adicionado ou removido alguma unidade de disco basta apenas atualizar a lista no módulo funcoes_move_videos.py obedecendo a ordem de hieraquia, o primeiroitem da lista tem prefencia sobre os outros.

        # Verificando se há espaço suficiente na unidade para realizar o transferencia de arquivos. Somente quanto o valor for True será liberado mover os arquivos.
        unidade_atual_armazenamento = fmv.unidade_atual()
        espaco_suficiente_em_disco = False  # Inicialmente, considero que não há espaço suficiente em disco.

        for unidade, espaco_disponivel in espaco_diponivel_unidade_de_disco.items():
            if tamanho_arquivos < espaco_disponivel:
                # Diretório de destino
                pasta_destino = os.path.join(unidade_atual_armazenamento, str(ano_atual), str(mes_atual) + " " + str(meses_do_ano[mes_atual]), f"{ano_atual:04}-{mes_atual:02}-{dia_atual:02}")

                # Caso não exista pasta de destino dos arquivos, ela será criada.
                if not os.path.exists(pasta_destino):
                    os.makedirs(pasta_destino)

                print(f'Unidade de destino atual: Disco {unidade}')

                # Crie a barra de progresso para este loop
                progress_bar = tqdm(arquivos_correspondentes_diretorio, dynamic_ncols=True)

                for arquivo in progress_bar:
                    try:
                        caminho_arquivo = os.path.join(pasta_destino, os.path.basename(arquivo))

                        if os.path.exists(caminho_arquivo) and os.path.isfile(caminho_arquivo):
                            # Se o arquivo já existe na pasta de destino, substitua-o pelo arquivo na pasta de origem
                            shutil.copy2(arquivo, caminho_arquivo)  # Use shutil.copy2 para manter metadados

                        else:
                            # Mover o arquivo da pasta de origem para a pasta de destino
                            shutil.move(arquivo, pasta_destino)

                        # Atualize a descrição da barra de progresso com o nome do arquivo atual
                        arquivo_nome = os.path.basename(arquivo)
                        progress_bar.set_description(f'Movendo arquivo {arquivo_nome} de vídeo para unidade {unidade}'.replace(':', ''))

                    except PermissionError as e:
                        msg = f"Erro de permissão ao mover o arquivo {os.path.basename(arquivo)}. Realizar transferência manualmente."
                        fmv.envia_msg_wpp(msg)

                espaco_suficiente_em_disco = True

            else:
                altera_unidade = fmv.alternar_unidade()
            break

        fmv.mover_arquivos_feito()

if not espaco_suficiente_em_disco:
    msg = f"*Erro*: Nenhuma unidade de disco com espaço livre suficiente para backup."
    fmv.envia_msg_wpp(msg)
