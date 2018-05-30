from classes import Escalonador as es
from classes import Processo as proc

# Organiza alocação e desalocação de memória e entrada/saída.

from classes.Escalonador import *
import time

# Constantes para requisição de recursos de E/S:
IMP = 0
SCN = 1
MDM = 2
CD = 3

NOVO = 0
PRONTO = 1
EXECUTANDO = 2
BLOQUEADO = 3
SUSPENSO = 4
TERMINADO = 5

class Sistema():
    # Construtor da classe.
    def __init__(self, totalRam=8192, totalImp=2, totalScn=1, totalMdm=1, totalCd=2):
        self.__totalRAM = totalRam
        self.__tempoAtual = 0
        self.__ramUsada = 0

        # Variável para controle que não será alterada após instanciamento da classe.
        self.__maximos = [totalImp, totalScn, totalMdm, totalCd]

        self.__esUsados = [0, 0, 0, 0]

        #Filas de estado:
        self.listaProntos = []
        self.listaExecutando = []
        self.listaBloqueados = []
        self.listaSuspensos = []
        self.listaTerminados = []

        # Variáveis para controle. Acho que poderá ser removido futuramente
        # self.totalProcessosProntos = 0
        # self.totalProcessosExecutando = 0
        # self.totalProcessosSuspensos = 0
        # self.totalProcessosTerminados = 0

    # Organiza o 'print' da classe:
    def __str__(self):
        return "RAM Livre: " + str(self.__totalRAM) + "\n" + "RAM Usada: " + str(self.__totalRAM) + "\n" + \
               "Processos Prontos: " + str(len(self.listaProntos)) + "\n" + "Processos Executando: " + \
               str(len(self.listaExecutando)) + "\n" + "Processos Suspensos: " + str(len(self.listaSuspensos)) + "\n" + \
               "Processos Terminados: " + str(len(self.listaTerminados)) + "\n"

    # Retorna a quantidade de memória RAM total:
    def pegaTotalRam(self):
        return self.__totalRAM

    # Retorna a quantidade de RAM usada atualmente:
    def pegaRamUsada(self):
        return self.__ramUsada

    #Atualiza os tempos totais de duração de todos os processos já submetidos e carrega em RAM processos novos que
    #possam ser carregados::
    def atualizaProcessos(self, esc):
        #print("Em atualizaProcessos()")

        for pr in self.listaBloqueados:
            pr.incrementaTempoTotal(1)
            self.atualizaEstado(pr, esc)
        for pr in self.listaSuspensos:
            pr.incrementaTempoTotal(1)
            self.atualizaEstado(pr, esc)

        #esc.imprimeFila(self.listaBloqueados, 66)
        #esc.imprimeFila(self.listaSuspensos, 67)

        for fila in esc.filas[:]:
            for pr in fila[:]:
                pr.incrementaTempoTotal(1)

                # if (pr.pegaEstado() == pr.BLOQUEADO):
                #     if pr not in self.listaBloqueados:
                #         esc.filas[pr.pegaPrioridade()].remove(pr)
                #         self.listaBloqueados.append(pr)
                # if (pr.pegaEstado() == pr.SUSPENSO):
                #     if pr not in self.listaSuspensos:
                #         esc.filas[pr.pegaPrioridade()].remove(pr)
                #         self.listaSuspensos.append(pr)
                self.atualizaEstado(pr, esc)

        #for i in range(len(esc.filas)): esc.imprimeFila(esc.filas[i], i)

        return

    #Executa um processo, ordenando que o escalonador orquestre a execução do mesmo:
    def executa(self, esc):
        self.atualizaProcessos(esc)
        proc = self.escolheProcesso(esc)
        #print("Entrou no executa() " + str(proc))
        time.sleep(0.3)
        if (proc != None):
            print(proc)
            if (proc.pegaEstado() == proc.PRONTO):
                self.listaProntos.remove(proc)
                proc.setaEstado(proc.EXECUTANDO)
                proc.setaTempoInicio(self.__tempoAtual)
                self.listaExecutando.append(proc)
                if (proc.pegaId() == "U-1"): print("CHEGOU AQUI O CARA: " + str(proc))
                esc.escalona(proc, self.__tempoAtual)
            if (proc.pegaEstado() == proc.EXECUTANDO): esc.escalona(proc, self.__tempoAtual)
            if (proc.pegaEstado() == proc.TERMINADO):
                print("Processo " + proc.pegaId() + " terminado\n")
                self.listaExecutando.remove(proc)
                self.desalocaES(proc)
                self.desalocaMemoria(proc)
                proc.setaTempoFim(self.__tempoAtual)
                if (proc in esc.filas[proc.pegaPrioridade()]): esc.filas[proc.pegaPrioridade()].remove(proc)
                #for i in range(len(esc.filas[:])):
                #    if (proc in esc.filas[i]): esc.filas[i].remove(proc)
                self.listaTerminados.append(proc)
        self.__tempoAtual += 1
        return

    #Escolhe um processo para execução:
    def escolheProcesso(self, esc):
        #print("Em escolheProcesso():")
        #for i in range(len(esc.filas)): esc.imprimeFila(esc.filas[i], i)
        for i in range(len(esc.filas)):
            #print("Índice: " + str(i))
            if (len(esc.filas[i]) > 0):
                # if (esc.filas[i][0].pegaId() == "U-4"):
                #    print(esc.filas[i][0])
                #    break
                if (esc.filas[i][0].pegaEstado() == esc.filas[i][0].PRONTO) or \
                    (esc.filas[i][0].pegaEstado() == esc.filas[i][0].EXECUTANDO):
                    #print("escolheProcesso() escolheu: " + str(esc.filas[i][0]))
                    return esc.filas[i][0]
        return None

    #Atualiza o estado de um processo conforme suas demandas por RAM e E/S são atendidas num dado momento.
    def atualizaEstado(self, pr, esc):
        #print("Em atualizaEstado()")
        #if (pr.pegaId() == "U-1"): print("O ALEMAO TA AQUI: " + str(pr) + ", lista E/S: "+ str(pr.pegaNumDePerifericos()))

        if (pr.pegaEstado() == pr.BLOQUEADO): self.alocaESEReorganiza(pr, esc)

        if (pr.pegaEstado() == pr.SUSPENSO) or (pr.pegaEstado() == pr.NOVO):
            self.alocaMemoria(pr)
            if (pr.ramFoiAlocada()): self.alocaESEReorganiza(pr, esc)
            # if (pr.pegaEstado() == pr.NOVO) and (not pr.ramFoiAlocada()):  # Nesse caso, o processo não pôde ser alocado em RAM e algum processo (provavelmente mais antigo)
            #     # deve ser suspenso para que o novo processo pronto seja alocado.
            #     for bloq in self.listaBloqueados[:]:
            #         if (bloq.pegaMemoriaOcupada() >= pr.pegaMemoriaOcupada()):
            #             #self.listaBloqueados.remove(bloq)
            #             self.desalocaMemoria(bloq)
            #             bloq.setaEstado(bloq.SUSPENSO)
            #             #self.listaSuspensos.append(bloq)
            #             self.alocaMemoria(pr)
            #             #if (pr.ramFoiAlocada()): self.alocaESEReorganiza(pr, esc)
            #             break
        return pr

    #Ordena a alocação de dispositivos E/S a um processo e a transferência desse processo entre filas de prioridade.
    def alocaESEReorganiza(self, processo, esc):
        #print("Em alocaESEReorganiza()")
        #if (processo.pegaId() == "U-1"): print("ALEMAO TA AQUI: " + str(processo))
        #if (processo.pegaEstado() == processo.SUSPENSO): self.listaSuspensos.remove(processo)
        self.requisitaES(processo)
        if (processo.esFoiAlocada()):
            #if (processo.pegaId() == "U-1"): print("ALEMAO CHEIROU COCA: " + str(processo))
            if (processo.pegaEstado() == processo.BLOQUEADO):
                if (processo in self.listaBloqueados): self.listaBloqueados.remove(processo)
            processo.setaEstado(processo.PRONTO)
            if (processo not in esc.filas[processo.pegaPrioridade()]): esc.filas[processo.pegaPrioridade()].append(processo)
            if (processo not in self.listaProntos): self.listaProntos.append(processo)

            #print("OS TERCEIRO TÃO LEVANDO TIRO")
            print(processo)
            esc.imprimeFila(esc.filas[processo.pegaPrioridade()], processo.pegaPrioridade())
        else:
            #print("Proc. bloq.: " + str(processo))
            #if (processo.pegaEstado() != processo.BLOQUEADO):
                processo.setaEstado(processo.BLOQUEADO)
                if (processo not in self.listaBloqueados): self.listaBloqueados.append(processo)
                if (processo in esc.filas[processo.pegaPrioridade()]): esc.filas[processo.pegaPrioridade()].remove(processo)
                # for fila in esc.filas[:]:
                #     if processo in fila[:]:
                #         fila.remove(processo)

    # Aloca memória RAM a um processo.
    def alocaMemoria(self, processo):
        if (not processo.ramFoiAlocada()):
            if (processo.pegaEstado() == processo.NOVO) or (processo.pegaEstado() == processo.SUSPENSO):
                if (processo.pegaMemoriaOcupada() + self.__ramUsada) <= self.__totalRAM:
                    self.__ramUsada += processo.pegaMemoriaOcupada()
                    processo.setaEstadoAlocacaoRam(True)
                    return True, processo
            print("Erro ao tentar alocar RAM: processo " + processo.pegaId())
            return False, processo

    # Operação simétrica à anterior.
    def desalocaMemoria(self, processo):
        if (processo.ramFoiAlocada()):
            if (processo.pegaEstado() == processo.TERMINADO) or (processo.pegaEstado() == processo.BLOQUEADO):
                if ((self.__ramUsada - processo.pegaMemoriaOcupada()) >= 0):
                    self.__ramUsada -= processo.pegaMemoriaOcupada()
                    processo.setaEstadoAlocacaoRam(False)
                    return True, processo
                else:
                    print("Erro ao tentar desalocar RAM: processo " + processo.pegaId())
                    return False, processo
            else: return False, processo

    # Aloca recursos de E/S de um processo:
    def requisitaES(self, processo):
        if (not processo.esFoiAlocada()):
            listaES = processo.pegaNumDePerifericos()
            if (processo.pegaEstado() == processo.NOVO) or (processo.pegaEstado() == processo.SUSPENSO) or \
                    (processo.pegaEstado() == processo.BLOQUEADO):
                cont = 0
                for i in range(len(listaES)):
                    if ((self.__esUsados[i] + listaES[i]) <= self.__maximos[i]): cont += 1
                    else: break
                if (cont == 4):
                    for i in range(len(self.__esUsados[:])): self.__esUsados[i] += listaES[i]
                    processo.setaEstadoAlocacaoES(True)
                    return True, processo
                else:
                    print("Erro em requisição de E/S: processo " + processo.pegaId())
                    return False, processo

    # Desaloca recursos de E/S de um processo:
    def desalocaES(self, processo):
        if (processo.esFoiAlocada()):
            listaES = processo.pegaNumDePerifericos()
            if (processo.pegaEstado() == processo.TERMINADO):
                cont = 0
                for i in range(len(listaES)):
                    if ((self.__esUsados[i] - listaES[i]) >= 0): cont += 1
                    else: break
                if (cont == 4):
                    for i in range(len(self.__esUsados[:])): self.__esUsados[i] -= listaES[i]
                    processo.setaEstadoAlocacaoES(False)
                    return True, processo
                else:
                    print("Erro em desalocação de E/S: processo " + processo.pegaId())
                    return False, processo

    # Retorna a qtd. de dispositivos E/S livres:
    def dispositivosESLivres(self, cod):
        if (cod >= 0) and (cod < 4):
            return self.__maximos[cod] - self.__esUsados[cod]

    # Retorna a qtd. de RAM livre:
    def pegaMemoriaLivre(self):
        return self.__totalRAM - self.__ramUsada

    #Retorna o tempo atual do sistema:
    def pegaTempoAtual(self):
        return self.__tempoAtual