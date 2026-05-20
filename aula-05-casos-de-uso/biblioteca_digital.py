"""
Biblioteca Digital — Casos de Uso
Aula 05 - UML e Casos de Uso

Parte 1: Modelos Livro e Usuario
Parte 2: Operações de empréstimo e reserva
Parte 3: Sistema completo com notificações e relatório de acervo
"""

from datetime import date, timedelta
from typing import Optional

# ─────────────────────────────────────────
# PARTE 1 — Modelos Livro e Usuario
# ─────────────────────────────────────────

class Livro:
    """
    Representa um livro no acervo da biblioteca.
    Caso de Uso: UC-01 Buscar Livro, UC-02 Reservar Livro.
    """

    def __init__(self, isbn: str, titulo: str, autor: str, ano: int, exemplares: int = 1):
        if exemplares < 0:
            raise ValueError("Número de exemplares não pode ser negativo.")
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.exemplares_total = exemplares
        self.exemplares_disponiveis = exemplares
        self.lista_espera: list[str] = []  # fila de usuário_id aguardando

    def esta_disponivel(self) -> bool:
        return self.exemplares_disponiveis > 0

    def __repr__(self):
        status = "disponível" if self.esta_disponivel() else "indisponível"
        return f"Livro({self.titulo!r}, {self.autor}, {status})"


class Usuario:
    """
    Representa um membro cadastrado na biblioteca.
    Caso de Uso: UC-05 Gerenciar Acervo (pelo bibliotecário).
    """

    LIMITE_EMPRESTIMOS = 3
    TIPOS_VALIDOS = ["leitor", "bibliotecario", "administrador"]

    def __init__(self, id_: str, nome: str, email: str, tipo: str = "leitor"):
        if tipo not in self.TIPOS_VALIDOS:
            raise ValueError(f"Tipo inválido. Opções: {self.TIPOS_VALIDOS}")
        self.id = id_
        self.nome = nome
        self.email = email
        self.tipo = tipo
        self.emprestimos_ativos: list[str] = []  # lista de ISBNs

    def pode_emprestar(self) -> bool:
        return len(self.emprestimos_ativos) < self.LIMITE_EMPRESTIMOS

    def __repr__(self):
        return f"Usuario({self.nome!r}, {self.tipo}, empréstimos={len(self.emprestimos_ativos)})"


# ─────────────────────────────────────────
# PARTE 2 — Operações de empréstimo e reserva
# ─────────────────────────────────────────

class Emprestimo:
    """
    Registra um empréstimo ativo.
    Caso de Uso: UC-03 Fazer Empréstimo, UC-04 Devolver Livro.
    """

    PRAZO_DIAS = 14

    def __init__(self, usuario: Usuario, livro: Livro):
        self.usuario = usuario
        self.livro = livro
        self.data_retirada: date = date.today()
        self.data_devolucao_prevista: date = date.today() + timedelta(days=self.PRAZO_DIAS)
        self.devolvido: bool = False

    def devolver(self) -> int:
        """Registra devolução e retorna dias de atraso (0 se em dia)."""
        if self.devolvido:
            raise RuntimeError("Livro já foi devolvido.")
        self.devolvido = True
        atraso = (date.today() - self.data_devolucao_prevista).days
        return max(0, atraso)

    def __repr__(self):
        estado = "devolvido" if self.devolvido else f"devolução: {self.data_devolucao_prevista}"
        return f"Emprestimo({self.livro.titulo!r} → {self.usuario.nome}, {estado})"


# ─────────────────────────────────────────
# PARTE 3 — Sistema completo com notificações e relatório
# ─────────────────────────────────────────

class BibliotecaDigital:
    """
    Sistema central da Biblioteca Digital.
    Implementa todos os casos de uso do diagrama UML.
    """

    def __init__(self, nome: str):
        self.nome = nome
        self.acervo: dict[str, Livro] = {}        # isbn -> Livro
        self.usuarios: dict[str, Usuario] = {}    # id -> Usuario
        self.emprestimos: list[Emprestimo] = []
        self._notificacoes: list[str] = []        # log de notificações

    # ── Gerenciamento do acervo (UC-05) ──────────────────

    def cadastrar_livro(self, livro: Livro) -> None:
        if livro.isbn in self.acervo:
            raise ValueError(f"ISBN {livro.isbn} já cadastrado.")
        self.acervo[livro.isbn] = livro
        print(f"[ACERVO] '{livro.titulo}' cadastrado ({livro.exemplares_total} exemplar(es)).")

    def cadastrar_usuario(self, usuario: Usuario) -> None:
        if usuario.id in self.usuarios:
            raise ValueError(f"Usuário ID {usuario.id} já cadastrado.")
        self.usuarios[usuario.id] = usuario
        print(f"[USUÁRIO] {usuario.nome} ({usuario.tipo}) cadastrado.")

    # ── Busca (UC-01) ─────────────────────────────────────

    def buscar_livro(self, termo: str) -> list[Livro]:
        """Busca por título ou autor (case-insensitive)."""
        termo_lower = termo.lower()
        resultados = [
            livro for livro in self.acervo.values()
            if termo_lower in livro.titulo.lower() or termo_lower in livro.autor.lower()
        ]
        if resultados:
            print(f"\n[BUSCA] '{termo}' — {len(resultados)} resultado(s):")
            for l in resultados:
                disp = "disponível" if l.esta_disponivel() else f"indisponível (fila: {len(l.lista_espera)})"
                print(f"  • {l.titulo} — {l.autor} [{disp}]")
        else:
            print(f"[BUSCA] Nenhum resultado para '{termo}'.")
        return resultados

    # ── Reserva (UC-02) ───────────────────────────────────

    def reservar_livro(self, usuario_id: str, isbn: str) -> None:
        """Coloca usuário na fila de espera do livro (UC-02 + extend Notificar)."""
        usuario = self._obter_usuario(usuario_id)
        livro = self._obter_livro(isbn)

        if usuario_id in livro.lista_espera:
            raise ValueError(f"{usuario.nome} já está na lista de espera.")
        if livro.esta_disponivel():
            print(f"[RESERVA] '{livro.titulo}' está disponível — realize o empréstimo diretamente.")
            return

        livro.lista_espera.append(usuario_id)
        print(f"[RESERVA] {usuario.nome} adicionado à fila de '{livro.titulo}' "
              f"(posição {len(livro.lista_espera)}).")

    # ── Empréstimo (UC-03) ────────────────────────────────

    def fazer_emprestimo(self, usuario_id: str, isbn: str) -> Emprestimo:
        usuario = self._obter_usuario(usuario_id)
        livro = self._obter_livro(isbn)

        if not usuario.pode_emprestar():
            raise RuntimeError(f"{usuario.nome} atingiu o limite de {Usuario.LIMITE_EMPRESTIMOS} empréstimos.")
        if not livro.esta_disponivel():
            raise RuntimeError(f"'{livro.titulo}' não possui exemplares disponíveis.")

        livro.exemplares_disponiveis -= 1
        usuario.emprestimos_ativos.append(isbn)

        emp = Emprestimo(usuario, livro)
        self.emprestimos.append(emp)

        print(f"[EMPRÉSTIMO] '{livro.titulo}' emprestado a {usuario.nome}. "
              f"Devolução até {emp.data_devolucao_prevista}.")
        return emp

    # ── Devolução (UC-04) ─────────────────────────────────

    def devolver_livro(self, usuario_id: str, isbn: str) -> None:
        usuario = self._obter_usuario(usuario_id)
        livro = self._obter_livro(isbn)

        # localiza empréstimo ativo
        emp = next(
            (e for e in self.emprestimos
             if e.usuario.id == usuario_id and e.livro.isbn == isbn and not e.devolvido),
            None
        )
        if not emp:
            raise RuntimeError("Empréstimo ativo não encontrado.")

        atraso = emp.devolver()
        livro.exemplares_disponiveis += 1
        usuario.emprestimos_ativos.remove(isbn)

        if atraso > 0:
            print(f"[DEVOLUÇÃO] '{livro.titulo}' devolvido por {usuario.nome} "
                  f"com {atraso} dia(s) de atraso.")
        else:
            print(f"[DEVOLUÇÃO] '{livro.titulo}' devolvido por {usuario.nome} no prazo.")

        # notifica próximo da fila (<<extend>> UC-02)
        self._notificar_proximo_da_fila(livro)

    def _notificar_proximo_da_fila(self, livro: Livro) -> None:
        """Notifica o primeiro da lista de espera quando um exemplar fica disponível."""
        if livro.lista_espera:
            proximo_id = livro.lista_espera.pop(0)
            usuario = self.usuarios.get(proximo_id)
            if usuario:
                msg = (f"[NOTIFICAÇÃO] {usuario.nome} ({usuario.email}): "
                       f"'{livro.titulo}' está disponível para retirada!")
                self._notificacoes.append(msg)
                print(msg)

    # ── Relatório do acervo ───────────────────────────────

    def relatorio_acervo(self) -> None:
        print(f"\n{'=' * 60}")
        print(f"  ACERVO — {self.nome}")
        print(f"{'=' * 60}")
        print(f"  Total de títulos: {len(self.acervo)}")
        print(f"  Total de usuários: {len(self.usuarios)}")
        print(f"  Total de empréstimos realizados: {len(self.emprestimos)}")

        ativos = [e for e in self.emprestimos if not e.devolvido]
        print(f"  Empréstimos ativos: {len(ativos)}")

        print(f"\n  Livros:")
        for livro in self.acervo.values():
            fila = f"fila={len(livro.lista_espera)}" if livro.lista_espera else ""
            print(f"    • {livro.titulo:35s} disp: {livro.exemplares_disponiveis}/"
                  f"{livro.exemplares_total}  {fila}")
        print(f"{'=' * 60}")

    # ── Helpers privados ──────────────────────────────────

    def _obter_livro(self, isbn: str) -> Livro:
        if isbn not in self.acervo:
            raise KeyError(f"Livro ISBN {isbn} não encontrado.")
        return self.acervo[isbn]

    def _obter_usuario(self, usuario_id: str) -> Usuario:
        if usuario_id not in self.usuarios:
            raise KeyError(f"Usuário ID {usuario_id} não encontrado.")
        return self.usuarios[usuario_id]


# ─────────────────────────────────────────
# DEMONSTRAÇÃO
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== Biblioteca Digital FIAP ===\n")

    bib = BibliotecaDigital("Biblioteca FIAP")

    # Parte 1: criação de livros e usuários
    print("--- Parte 1: Cadastro ---")
    bib.cadastrar_livro(Livro("978-0-13-468599-1", "Clean Code", "Robert C. Martin", 2008, 2))
    bib.cadastrar_livro(Livro("978-0-13-235088-4", "The Pragmatic Programmer", "David Thomas", 2019, 1))
    bib.cadastrar_livro(Livro("978-0-20-163361-0", "Design Patterns", "Gang of Four", 1994, 1))

    bib.cadastrar_usuario(Usuario("U001", "Alice Ferreira",  "alice@fiap.com",  "leitor"))
    bib.cadastrar_usuario(Usuario("U002", "Bruno Costa",    "bruno@fiap.com",  "leitor"))
    bib.cadastrar_usuario(Usuario("U003", "Carla Mendes",   "carla@fiap.com",  "bibliotecario"))

    # Parte 2: busca, reserva e empréstimo
    print("\n--- Parte 2: Operações ---")
    bib.buscar_livro("clean")
    bib.buscar_livro("patterns")

    emp1 = bib.fazer_emprestimo("U001", "978-0-20-163361-0")  # Design Patterns — 1 exemplar
    emp2 = bib.fazer_emprestimo("U002", "978-0-13-235088-4")  # Pragmatic Programmer

    bib.reservar_livro("U003", "978-0-20-163361-0")  # Carla entra na fila de Design Patterns

    # Parte 3: devolução com notificação + relatório
    print("\n--- Parte 3: Devolução e Notificação ---")
    bib.devolver_livro("U001", "978-0-20-163361-0")  # Alice devolve → Carla é notificada

    bib.relatorio_acervo()
