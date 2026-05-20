"""
Transferência Nubank — Diagrama de Sequência
Aula 07 - Diagramas de Sequência

Simula as mensagens entre os participantes do diagrama:
  1. Usuário
  2. App Nubank
  3. Serviço de Autenticação
  4. Serviço de Transferência
  5. Banco Central (BACEN)
"""

from datetime import datetime
from enum import Enum


# ─────────────────────────────────────────
# Tipos e modelos de suporte
# ─────────────────────────────────────────

class StatusTransferencia(Enum):
    PENDENTE = "Pendente"
    AUTENTICADA = "Autenticada"
    APROVADA = "Aprovada"
    CONCLUIDA = "Concluída"
    FALHA = "Falha"


class Conta:
    """Representa a conta bancária de um usuário."""

    def __init__(self, numero: str, titular: str, saldo: float):
        if saldo < 0:
            raise ValueError("Saldo inicial não pode ser negativo.")
        self.numero = numero
        self.titular = titular
        self._saldo = saldo
        self.historico: list[dict] = []

    @property
    def saldo(self) -> float:
        return self._saldo

    def debitar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor de débito deve ser positivo.")
        if self._saldo < valor:
            raise RuntimeError(
                f"Saldo insuficiente: disponível R${self._saldo:.2f}, solicitado R${valor:.2f}."
            )
        self._saldo -= valor

    def creditar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor de crédito deve ser positivo.")
        self._saldo += valor

    def registrar(self, descricao: str, valor: float) -> None:
        self.historico.append({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "descricao": descricao,
            "valor": valor,
            "saldo_apos": self._saldo,
        })

    def __repr__(self):
        return f"Conta({self.numero}, {self.titular}, R${self._saldo:.2f})"


# ─────────────────────────────────────────
# Participantes do diagrama de sequência
# ─────────────────────────────────────────

class ServicoAutenticacao:
    """
    Participante: Serviço de Autenticação
    Mensagem recebida: validarToken(token)
    Mensagem retornada: tokenValido / tokenInvalido
    """

    TOKENS_VALIDOS = {"tok_alice_001", "tok_bruno_002"}

    def validar_token(self, token: str) -> bool:
        valido = token in self.TOKENS_VALIDOS
        status = "válido" if valido else "inválido"
        print(f"  [Serviço Autenticação] validarToken({token!r}) → {status}")
        return valido


class BancoCentral:
    """
    Participante: Banco Central (BACEN)
    Mensagem recebida: processarTransferencia(dados)
    Mensagem retornada: confirmacao / erro
    """

    _protocolo_seq = 0

    @classmethod
    def processar_transferencia(cls, origem: str, destino: str, valor: float) -> str:
        cls._protocolo_seq += 1
        protocolo = f"BACEN-{cls._protocolo_seq:06d}"
        print(f"  [Banco Central] processarTransferencia("
              f"origem={origem}, destino={destino}, valor=R${valor:.2f}) "
              f"→ protocolo={protocolo}")
        return protocolo


class ServicoTransferencia:
    """
    Participante: Serviço de Transferência
    Mensagens: verificarSaldo, debitarConta, creditarConta, notificarPartes
    """

    def __init__(self, banco_central: BancoCentral):
        self._bacen = banco_central

    def verificar_saldo(self, conta: Conta, valor: float) -> bool:
        tem_saldo = conta.saldo >= valor
        status = "suficiente" if tem_saldo else "insuficiente"
        print(f"  [Serviço Transferência] verificarSaldo("
              f"{conta.numero}, R${valor:.2f}) → {status} (disponível: R${conta.saldo:.2f})")
        return tem_saldo

    def executar(self, conta_origem: Conta, conta_destino: Conta, valor: float) -> str:
        """
        Realiza débito, crédito e aciona o BACEN.
        Corresponde ao bloco 'loop' + mensagens síncronas do diagrama.
        """
        conta_origem.debitar(valor)
        conta_origem.registrar(f"Transferência para {conta_destino.titular}", -valor)
        print(f"  [Serviço Transferência] debitarConta({conta_origem.numero}, R${valor:.2f}) → ok")

        conta_destino.creditar(valor)
        conta_destino.registrar(f"Recebido de {conta_origem.titular}", valor)
        print(f"  [Serviço Transferência] creditarConta({conta_destino.numero}, R${valor:.2f}) → ok")

        protocolo = self._bacen.processar_transferencia(
            conta_origem.numero, conta_destino.numero, valor
        )
        return protocolo

    def notificar(self, conta_origem: Conta, conta_destino: Conta, valor: float, protocolo: str) -> None:
        print(f"  [Serviço Transferência] notificarPartes → "
              f"{conta_origem.titular} e {conta_destino.titular} notificados "
              f"(protocolo {protocolo})")


class AppNubank:
    """
    Participante: App Nubank
    Orquestra as chamadas entre os demais participantes,
    espelhando o objeto central do diagrama de sequência.
    """

    def __init__(self):
        self._auth = ServicoAutenticacao()
        self._bacen = BancoCentral()
        self._transferencia = ServicoTransferencia(self._bacen)

    def solicitar_transferencia(
        self,
        token: str,
        conta_origem: Conta,
        conta_destino: Conta,
        valor: float,
    ) -> dict:
        """
        Fluxo principal do diagrama de sequência:
        Usuário → App → Autenticação → Transferência → BACEN → App → Usuário
        """
        print(f"\n{'─' * 60}")
        print(f"  [Usuário → App] solicitarTransferencia("
              f"R${valor:.2f} para {conta_destino.titular})")
        print(f"{'─' * 60}")

        resultado = {
            "valor": valor,
            "origem": conta_origem.numero,
            "destino": conta_destino.numero,
            "status": StatusTransferencia.PENDENTE,
            "protocolo": None,
            "mensagem": "",
        }

        # 1. Autenticação (alt: token válido / inválido)
        print("\n  → autenticarUsuario(token)")
        if not self._auth.validar_token(token):
            resultado["status"] = StatusTransferencia.FALHA
            resultado["mensagem"] = "Autenticação falhou: token inválido."
            print(f"\n  [App → Usuário] ERRO: {resultado['mensagem']}")
            return resultado

        resultado["status"] = StatusTransferencia.AUTENTICADA

        # 2. Verificar saldo (loop do diagrama)
        print("\n  → verificarSaldo")
        if not self._transferencia.verificar_saldo(conta_origem, valor):
            resultado["status"] = StatusTransferencia.FALHA
            resultado["mensagem"] = (
                f"Saldo insuficiente: disponível R${conta_origem.saldo:.2f}, "
                f"solicitado R${valor:.2f}."
            )
            print(f"\n  [App → Usuário] ERRO: {resultado['mensagem']}")
            return resultado

        resultado["status"] = StatusTransferencia.APROVADA

        # 3. Executar transferência e acionar BACEN
        print("\n  → executarTransferencia")
        protocolo = self._transferencia.executar(conta_origem, conta_destino, valor)
        resultado["protocolo"] = protocolo
        resultado["status"] = StatusTransferencia.CONCLUIDA

        # 4. Notificar partes
        print("\n  → notificarPartes")
        self._transferencia.notificar(conta_origem, conta_destino, valor, protocolo)

        resultado["mensagem"] = "Transferência realizada com sucesso."
        print(f"\n  [App → Usuário] OK: {resultado['mensagem']} Protocolo: {protocolo}")
        return resultado


# ─────────────────────────────────────────
# DEMONSTRAÇÃO
# ─────────────────────────────────────────

def exibir_extrato(conta: Conta) -> None:
    print(f"\n  Extrato de {conta.titular} ({conta.numero})  saldo: R${conta.saldo:.2f}")
    for mov in conta.historico:
        sinal = "+" if mov["valor"] > 0 else ""
        print(f"    {mov['data']}  {mov['descricao']:40s}  {sinal}R${mov['valor']:.2f}")


if __name__ == "__main__":
    print("=== Transferência Nubank — Diagrama de Sequência ===")

    app = AppNubank()

    alice = Conta("0001-7", "Alice Ferreira", saldo=2500.00)
    bruno = Conta("0002-3", "Bruno Costa",    saldo=800.00)

    # Cenário 1: transferência bem-sucedida
    print("\n\n>>> Cenário 1: transferência bem-sucedida")
    app.solicitar_transferencia(
        token="tok_alice_001",
        conta_origem=alice,
        conta_destino=bruno,
        valor=500.00,
    )

    # Cenário 2: saldo insuficiente
    print("\n\n>>> Cenário 2: saldo insuficiente")
    app.solicitar_transferencia(
        token="tok_alice_001",
        conta_origem=alice,
        conta_destino=bruno,
        valor=9999.00,
    )

    # Cenário 3: token inválido (autenticação falha)
    print("\n\n>>> Cenário 3: token inválido")
    app.solicitar_transferencia(
        token="tok_INVALIDO",
        conta_origem=alice,
        conta_destino=bruno,
        valor=100.00,
    )

    # Extrato final
    print("\n\n>>> Extratos finais")
    exibir_extrato(alice)
    exibir_extrato(bruno)
