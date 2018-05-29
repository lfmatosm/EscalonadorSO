from classes import Processo as proc

# Responsável pelo escalonamento (execução, suspensão e término) de processos.
class Escalonador(object):
    def __init__(self, fTReal, fUs1, fUs2, fUs3):
        self.tAtual = 0
        self.pAtual = None
        self.totalQuantums = 2
        self.TR = 0
        self.U1 = 1
        self.U2 = 2
        self.U3 = 3
        self.filas = [fTReal, fUs1, fUs2, fUs3]

    #Responsável por escalonar um processo. Emprega "round robin" (fila de TR) e "feedback" (filas de prioridade de usuário) para isso.
    def escalona(self, p, tAtual):
        self.tAtual = tAtual
        if (p.pegaEstado() == p.EXECUTANDO):
            # Atualiza o tempo de execução do processo:
            p.incrementaTempoDeExecucao(1)
            if ((p.pegaTempoTotalExecutando() - 1) == p.pegaTempoDeServico()):
                p.setaTempoFim(tAtual)
                p.setaEstado(p.TERMINADO)
            #Para processos de usuário (prioridades 1-3):
            else:
                #Filas de prioridade de usuário. Seguem a política de escalonanamento "feedback", usando quantum = 2.
                executarTroca = False
                print("Quantum atual de "+str(p.pegaId())+": "+str(p.pegaQuantums()))
                if (p.pegaQuantums() < self.totalQuantums): p.incrementaQuantums(1)
                else:
                    p.setaQuantums(0)
                    executarTroca = True
                if (executarTroca):
                    self.filas[p.pegaPrioridade()].remove(p)
                    pNovaFila = (p.pegaPrioridade() % 3) + 1 #Calcula qual será a fila em que o processo será inserido com
                    #base na fila em que ele se encontra atualmente
                    p.setaPrioridade(pNovaFila)
                    self.filas[p.pegaPrioridade()].append(p) #Adiciona na próxima fila (política de feedback)
        print(p)
        if (p.pegaEstado() == p.TERMINADO): self.pAtual = None
        else: self.pAtual = p
        return p

    #Seleciona um determinado processo de uma das filas de prioridade conforme o parâmetro passado como índice para a função:
    def pegaProcesso(self, fila, indice):
        if fila == 0: return self.filas[self.TR][indice]
        elif fila == 1: return self.filas[self.U1][indice]
        elif fila == 1: return self.filas[self.U2][indice]
        else: return self.filas[self.U3][indice]