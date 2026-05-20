"""
Cadastro e Aprovação de Usuário
Aula 06 - Diagramas de Atividades

Espelha o diagrama de atividades com swimlanes:
  Raia 1 — Usuário: preenche e envia o formulário
  Raia 2 — Sistema: valida dados e gerencia estados
  Raia 3 — Administrador: aprova ou rejeita o cadastro
"""

import re
from enum import Enum
from datetime import datetime


# ─────────────────────────────────────────
# Estados do fluxo (swimlane Sistema)
# ─────────────────────────────────────────

class StatusCadastro(Enum):
    PENDENTE_VALIDACAO = "Pendente de Validação"
    AGUARDANDO_APROVACAO = "Aguardando Aprovação do Administrador"
    APROVADO = "Aprovado"
    REJEITADO = "Rejeitado"


# ─────────────────────────────────────────
# Modelo de Solicitação de Cadastro
# ─────────────────────────────────────────

class SolicitacaoCadastro:
    """Representa o formulário preenchido pelo usuário (Raia: Usuário)."""

    def __init__(self, nome: str, email: str, senha: str, perfil: str):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.perfil = perfil
        self.status = StatusCadastro.PENDENTE_VALIDACAO
        self.erros_validacao: list[str] = []
        self.criado_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.motivo_rejeicao: str = ""

    def __repr__(self):
        return f"Solicitacao({self.nome!r}, {self.email!r}, status={self.status.value})"


# ─────────────────────────────────────────
# Sistema — validação e gerenciamento de estado
# (Raia: Sistema)
# ─────────────────────────────────────────

PERFIS_VALIDOS = ["aluno", "professor", "funcionario"]


def validar_formulario(solicitacao: SolicitacaoCadastro) -> bool:
    """
    Valida os dados do formulário.
    Atividade do diagrama: 'Validar dados do formulário'.
    Retorna True se todos os dados são válidos.
    """
    erros = []

    # Validação do nome
    if len(solicitacao.nome.strip()) < 3:
        erros.append("Nome deve ter pelo menos 3 caracteres.")

    # Validação do e-mail
    padrao_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(padrao_email, solicitacao.email):
        erros.append("E-mail inválido.")

    # Validação da senha
    if len(solicitacao.senha) < 8:
        erros.append("Senha deve ter pelo menos 8 caracteres.")
    if not any(c.isdigit() for c in solicitacao.senha):
        erros.append("Senha deve conter pelo menos um número.")
    if not any(c.isupper() for c in solicitacao.senha):
        erros.append("Senha deve conter pelo menos uma letra maiúscula.")

    # Validação do perfil
    if solicitacao.perfil.lower() not in PERFIS_VALIDOS:
        erros.append(f"Perfil inválido. Opções: {PERFIS_VALIDOS}")

    solicitacao.erros_validacao = erros

    if erros:
        solicitacao.status = StatusCadastro.PENDENTE_VALIDACAO
        return False

    # Dados válidos — aguarda aprovação do administrador
    solicitacao.status = StatusCadastro.AGUARDANDO_APROVACAO
    return True


# ─────────────────────────────────────────
# Administrador — aprovação ou rejeição
# (Raia: Administrador)
# ─────────────────────────────────────────

def aprovar_cadastro(solicitacao: SolicitacaoCadastro, admin: str) -> None:
    """
    Administrador aprova o cadastro.
    Atividade do diagrama: 'Aprovar cadastro'.
    """
    if solicitacao.status != StatusCadastro.AGUARDANDO_APROVACAO:
        raise RuntimeError(
            f"Solicitação não está aguardando aprovação (status atual: {solicitacao.status.value})."
        )
    solicitacao.status = StatusCadastro.APROVADO
    print(f"[ADMIN: {admin}] Cadastro de '{solicitacao.nome}' APROVADO.")
    _notificar_usuario(solicitacao, aprovado=True)


def rejeitar_cadastro(solicitacao: SolicitacaoCadastro, admin: str, motivo: str) -> None:
    """
    Administrador rejeita o cadastro com justificativa.
    Atividade do diagrama: 'Rejeitar cadastro'.
    """
    if solicitacao.status != StatusCadastro.AGUARDANDO_APROVACAO:
        raise RuntimeError(
            f"Solicitação não está aguardando aprovação (status atual: {solicitacao.status.value})."
        )
    solicitacao.status = StatusCadastro.REJEITADO
    solicitacao.motivo_rejeicao = motivo
    print(f"[ADMIN: {admin}] Cadastro de '{solicitacao.nome}' REJEITADO. Motivo: {motivo}")
    _notificar_usuario(solicitacao, aprovado=False)


# ─────────────────────────────────────────
# Notificação (atividade final do fluxo)
# ─────────────────────────────────────────

def _notificar_usuario(solicitacao: SolicitacaoCadastro, aprovado: bool) -> None:
    """
    Notifica o usuário com o resultado do cadastro.
    Atividade do diagrama: 'Notificar usuário'.
    """
    if aprovado:
        print(f"[NOTIFICAÇÃO → {solicitacao.email}] Bem-vindo(a), {solicitacao.nome}! "
              "Seu cadastro foi aprovado.")
    else:
        print(f"[NOTIFICAÇÃO → {solicitacao.email}] Seu cadastro foi rejeitado. "
              f"Motivo: {solicitacao.motivo_rejeicao}")


# ─────────────────────────────────────────
# Fluxo completo (orquestra todas as raias)
# ─────────────────────────────────────────

class SistemaCadastro:
    """Orquestra o fluxo do diagrama de atividades."""

    def __init__(self):
        self.solicitacoes: list[SolicitacaoCadastro] = []

    def enviar_formulario(self, nome: str, email: str, senha: str, perfil: str) -> SolicitacaoCadastro:
        """
        Raia Usuário: preenche e envia o formulário.
        Raia Sistema: valida os dados e define próximo estado.
        """
        print(f"\n[USUÁRIO] Enviando formulário de cadastro para '{nome}'...")
        solicitacao = SolicitacaoCadastro(nome, email, senha, perfil)
        self.solicitacoes.append(solicitacao)

        valido = validar_formulario(solicitacao)

        if not valido:
            print(f"[SISTEMA] Dados inválidos. Erros encontrados:")
            for erro in solicitacao.erros_validacao:
                print(f"  ✗ {erro}")
            print(f"[SISTEMA] Formulário devolvido ao usuário para correção.")
        else:
            print(f"[SISTEMA] Dados válidos. Solicitação encaminhada para aprovação.")

        return solicitacao

    def listar_pendentes(self) -> list[SolicitacaoCadastro]:
        pendentes = [s for s in self.solicitacoes
                     if s.status == StatusCadastro.AGUARDANDO_APROVACAO]
        print(f"\n[ADMIN] Solicitações pendentes: {len(pendentes)}")
        for s in pendentes:
            print(f"  • {s.nome:20s} {s.email:25s} perfil={s.perfil}  enviado em {s.criado_em}")
        return pendentes

    def relatorio(self) -> None:
        print(f"\n{'=' * 55}")
        print("  RELATÓRIO DE CADASTROS")
        print(f"{'=' * 55}")
        contagem = {}
        for s in self.solicitacoes:
            contagem[s.status.value] = contagem.get(s.status.value, 0) + 1
        for status, qtd in contagem.items():
            print(f"  {status:40s}: {qtd}")
        print(f"{'=' * 55}")


# ─────────────────────────────────────────
# DEMONSTRAÇÃO
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== Sistema de Cadastro e Aprovação ===")

    sistema = SistemaCadastro()

    # Tentativa com dados inválidos (retorna ao usuário para correção)
    s1 = sistema.enviar_formulario("Jo", "email-invalido", "abc", "hacker")

    # Cadastro válido de aluno
    s2 = sistema.enviar_formulario("Maria Souza", "maria@fiap.com", "Fiap2026!", "aluno")

    # Cadastro válido de professor
    s3 = sistema.enviar_formulario("Prof. Lucas", "lucas@fiap.com", "Senha123", "professor")

    # Administrador vê pendentes e toma decisões
    sistema.listar_pendentes()

    aprovar_cadastro(s2, admin="Admin Carlos")
    rejeitar_cadastro(s3, admin="Admin Carlos", motivo="Documentação pendente.")

    # Tentativa de aprovar solicitação já aprovada
    try:
        aprovar_cadastro(s2, admin="Admin Carlos")
    except RuntimeError as e:
        print(f"\n[ERRO] {e}")

    sistema.relatorio()
