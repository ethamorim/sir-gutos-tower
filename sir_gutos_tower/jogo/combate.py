from random import choice

from .personagens.lutavel import Lutavel

from ..utils.exceptions.exceptions import JaEstaNaFestaError, JogadorSemPontosDeVidaError, NaoAcertouAtaqueError
from ..jogo.decisores.decisor_historia import DecisorHistoria


class Combate:

    def __init__(self):
        self.herois = []
        self.monstros = []
        self.tomador_decisoes = None

    def adicionar_heroi(self, heroi):
        for heroiNaFesta in self.herois:
            if heroi == heroiNaFesta:
                raise JaEstaNaFestaError

        if heroi.eh_jogador:
            self.tomador_decisoes = DecisorHistoria()
        self.herois.append(heroi)

    def adicionar_monstro(self, monstro):
        for monstroNaFesta in self.monstros:
            if monstro == monstroNaFesta:
                raise JaEstaNaFestaError

        self.monstros.append(monstro)

    def comecar(self):
        lutando = True

        if len(self.herois) == 1:
            print('Você se prepara para lutar.')

        while lutando:
            try:
                self.checar_status_dos_participantes()
            except JogadorSemPontosDeVidaError:
                print('\nVocê perdeu')
                return False

            print()
            for monstro in self.monstros:
                print(monstro.nome, str(monstro.vida) + ' HP')

            self.rodar_vez_dos_herois()
            self.rodar_vez_dos_inimigos()

    def checar_status_dos_participantes(self):
        for heroi in self.herois:
            if heroi.esta_esgotado:
                pov = self.decidir_pov_heroi(heroi)
                print(pov + ' está esgotado')

                if heroi.eh_jogador:
                    raise JogadorSemPontosDeVidaError

    def rodar_vez_dos_herois(self):
        if len(self.monstros) == 1:
            monstro = self.monstros[0]

        for heroi in self.herois:
            ataques = heroi.retornar_ataques()

            if heroi.eh_jogador:
                self.tomador_decisoes.novas_decisoes(ataques)

                self.tomador_decisoes.imprimir_decisoes()
                decisao = self.tomador_decisoes.tomar_decisao(heroi)

                try:
                    dialogo = heroi.lutar(decisao, self.herois, monstro)
                except NaoAcertouAtaqueError:
                    dialogo = '{jogador} errou'

                dialogo = self.tratar_dialogo_ataque_antes_de_imprimir(dialogo, heroi, monstro)
                self.imprimir_dialogo(dialogo)

    def rodar_vez_dos_inimigos(self):
        for inimigo in self.monstros:
            heroi_a_atacar = choice(self.herois)

            ataques = inimigo.retornar_ataques()
            ataque_escolhido = choice(list(ataques.keys()))

            if ataques[ataque_escolhido]['tipo'] == 'defesa':
                if 'defesa' in inimigo.acoes_previas and inimigo.acoes_previas[0] != 'defesa':
                    ataque_escolhido = '1'

            try:
                dialogo_monstro = inimigo.lutar(
                    ataque_escolhido, self.monstros, heroi_a_atacar)
            except NaoAcertouAtaqueError:
                dialogo_monstro = '{monstro} errou'

            dialogo_monstro = self.tratar_dialogo_ataque_antes_de_imprimir(
                dialogo_monstro, heroi_a_atacar, inimigo)
            self.imprimir_dialogo(dialogo_monstro)

    def tratar_dialogo_ataque_antes_de_imprimir(self, dialogo, heroi, monstro):
        if type(dialogo) == list:
            dialogos = []
            for d in dialogo:
                dialogos.append(
                    self.reescrever_placeholders_de_dialogo_ataque(d, heroi, monstro)
                )
            return dialogos
        else:
            dialogo = self.reescrever_placeholders_de_dialogo_ataque(dialogo, heroi, monstro)
            return dialogo

    def reescrever_placeholders_de_dialogo_ataque(self, dialogo, heroi, monstro):
        pov = self.decidir_pov_heroi(heroi)
        pov = self.minimizar_palavra_voce_caso_nao_no_inicio_da_frase(pov, dialogo)

        dialogo = dialogo.replace('{jogador}', pov)
        dialogo = dialogo.replace('{monstro}', monstro.nome)

        return dialogo

    def decidir_pov_heroi(self, heroi):
        pov = heroi.nome
        if heroi.eh_jogador:
            pov = 'Você'
        return pov

    def minimizar_palavra_voce_caso_nao_no_inicio_da_frase(self, pov, dialogo):
        if pov == 'Você' and not dialogo.startswith('{jogador}'):
            pov = pov.lower()
        return pov

    def imprimir_dialogo(self, dialogo):
        print()

        if type(dialogo) == list:
            for d in dialogo:
                print(d)
        else:
            print(dialogo)
