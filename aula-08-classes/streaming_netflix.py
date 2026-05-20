"""
Sistema de Streaming — Netflix
Aula 08 - Diagramas de Classes

Implementa a hierarquia do diagrama de classes:
  - Conteudo (classe base abstrata)
      ├── Filme
      └── Serie (com Episodio)
  - Usuario
      ├── Perfil (até 5 por usuário)
      ├── Assinatura (planos: básico, padrão, premium)
      └── Reproducao (histórico de visualizações)
  - CatalogoService (dependência de Usuario)
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum
from typing import Optional


# ─────────────────────────────────────────
# Enumerações e constantes
# ─────────────────────────────────────────

class PlanoAssinatura(Enum):
    BASICO = "Básico"       # 1 tela, SD
    PADRAO = "Padrão"       # 2 telas, Full HD
    PREMIUM = "Premium"     # 4 telas, 4K + downloads


TELAS_POR_PLANO = {
    PlanoAssinatura.BASICO:  1,
    PlanoAssinatura.PADRAO:  2,
    PlanoAssinatura.PREMIUM: 4,
}

PRECO_PLANO = {
    PlanoAssinatura.BASICO:  18.90,
    PlanoAssinatura.PADRAO:  34.90,
    PlanoAssinatura.PREMIUM: 55.90,
}


# ─────────────────────────────────────────
# Hierarquia de Conteúdo (herança)
# ─────────────────────────────────────────

class Conteudo(ABC):
    """
    Classe base abstrata para todo conteúdo do catálogo.
    Diagrama: Conteudo <<abstract>> com atributos id, titulo, genero, classificacao.
    """

    def __init__(self, id_: str, titulo: str, genero: str, classificacao: str, ano: int):
        self.id = id_
        self.titulo = titulo
        self.genero = genero
        self.classificacao = classificacao  # ex.: "L", "10", "14", "16", "18"
        self.ano = ano
        self.avaliacoes: list[float] = []

    @abstractmethod
    def duracao_total_min(self) -> int:
        """Duração total em minutos (polimorfismo)."""
        ...

    def avaliar(self, nota: float) -> None:
        if not 0.0 <= nota <= 5.0:
            raise ValueError("Nota deve estar entre 0.0 e 5.0.")
        self.avaliacoes.append(nota)

    @property
    def nota_media(self) -> Optional[float]:
        return round(sum(self.avaliacoes) / len(self.avaliacoes), 1) if self.avaliacoes else None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.titulo!r}, {self.ano})"


class Filme(Conteudo):
    """
    Herda de Conteudo.
    Atributo adicional: duracao_min (duração total em minutos).
    """

    def __init__(self, id_: str, titulo: str, genero: str,
                 classificacao: str, ano: int, duracao_min: int, diretor: str):
        super().__init__(id_, titulo, genero, classificacao, ano)
        if duracao_min <= 0:
            raise ValueError("Duração deve ser positiva.")
        self._duracao_min = duracao_min
        self.diretor = diretor

    def duracao_total_min(self) -> int:
        return self._duracao_min


class Episodio:
    """Compõe a classe Serie (associação de composição no diagrama)."""

    def __init__(self, numero: int, titulo: str, duracao_min: int):
        self.numero = numero
        self.titulo = titulo
        self.duracao_min = duracao_min

    def __repr__(self):
        return f"Ep{self.numero:02d}: {self.titulo} ({self.duracao_min} min)"


class Serie(Conteudo):
    """
    Herda de Conteudo.
    Composição: uma Serie possui múltiplos Episodios por temporada.
    """

    def __init__(self, id_: str, titulo: str, genero: str,
                 classificacao: str, ano: int):
        super().__init__(id_, titulo, genero, classificacao, ano)
        self.temporadas: dict[int, list[Episodio]] = {}

    def adicionar_episodio(self, temporada: int, episodio: Episodio) -> None:
        self.temporadas.setdefault(temporada, []).append(episodio)

    def duracao_total_min(self) -> int:
        return sum(
            ep.duracao_min
            for eps in self.temporadas.values()
            for ep in eps
        )

    @property
    def total_episodios(self) -> int:
        return sum(len(eps) for eps in self.temporadas.values())


# ─────────────────────────────────────────
# Assinatura
# ─────────────────────────────────────────

class Assinatura:
    """
    Associação: Usuario possui uma Assinatura ativa por vez.
    Diagrama: Assinatura(plano, data_inicio, ativa).
    """

    def __init__(self, plano: PlanoAssinatura):
        self.plano = plano
        self.data_inicio = date.today()
        self.ativa = True

    @property
    def telas_simultaneas(self) -> int:
        return TELAS_POR_PLANO[self.plano]

    @property
    def preco_mensal(self) -> float:
        return PRECO_PLANO[self.plano]

    def cancelar(self) -> None:
        self.ativa = False

    def __repr__(self):
        estado = "ativa" if self.ativa else "cancelada"
        return f"Assinatura({self.plano.value}, R${self.preco_mensal:.2f}/mês, {estado})"


# ─────────────────────────────────────────
# Perfil
# ─────────────────────────────────────────

class Perfil:
    """
    Associação: Usuario possui até 5 Perfis.
    Diagrama: Perfil(nome, avatar, classificacao_maxima).
    """

    LIMITE_PERFIS = 5

    def __init__(self, nome: str, avatar: str = "default", classificacao_maxima: str = "18"):
        self.nome = nome
        self.avatar = avatar
        self.classificacao_maxima = classificacao_maxima

    def __repr__(self):
        return f"Perfil({self.nome!r}, classificacao_max={self.classificacao_maxima})"


# ─────────────────────────────────────────
# Reprodução (histórico)
# ─────────────────────────────────────────

class Reproducao:
    """
    Associação: registra cada reprodução de um conteúdo por um perfil.
    Diagrama: Reproducao(conteudo, perfil, progresso_pct, timestamp).
    """

    def __init__(self, conteudo: Conteudo, perfil: Perfil, progresso_pct: float = 0.0):
        if not 0.0 <= progresso_pct <= 100.0:
            raise ValueError("Progresso deve estar entre 0 e 100%.")
        self.conteudo = conteudo
        self.perfil = perfil
        self.progresso_pct = progresso_pct
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.concluido = progresso_pct >= 95.0

    def atualizar_progresso(self, pct: float) -> None:
        if not 0.0 <= pct <= 100.0:
            raise ValueError("Progresso deve estar entre 0 e 100%.")
        self.progresso_pct = pct
        self.concluido = pct >= 95.0

    def __repr__(self):
        return (f"Reproducao({self.conteudo.titulo!r}, perfil={self.perfil.nome}, "
                f"{self.progresso_pct:.0f}%)")


# ─────────────────────────────────────────
# Usuário
# ─────────────────────────────────────────

class Usuario:
    """
    Classe central do diagrama.
    Associações: Assinatura (1), Perfil (1..5), Reproducao (0..*).
    """

    def __init__(self, id_: str, nome: str, email: str, plano: PlanoAssinatura):
        self.id = id_
        self.nome = nome
        self.email = email
        self.assinatura = Assinatura(plano)
        self.perfis: list[Perfil] = []
        self.historico: list[Reproducao] = []

    def adicionar_perfil(self, perfil: Perfil) -> None:
        if len(self.perfis) >= Perfil.LIMITE_PERFIS:
            raise RuntimeError("Limite de 5 perfis atingido.")
        self.perfis.append(perfil)
        print(f"[PERFIL] '{perfil.nome}' adicionado à conta de {self.nome}.")

    def reproduzir(self, conteudo: Conteudo, perfil: Perfil,
                   progresso_pct: float = 0.0) -> Reproducao:
        if perfil not in self.perfis:
            raise ValueError("Perfil não pertence a esta conta.")
        rep = Reproducao(conteudo, perfil, progresso_pct)
        self.historico.append(rep)
        status = "concluído" if rep.concluido else f"{progresso_pct:.0f}%"
        print(f"[PLAY] {perfil.nome} assistiu '{conteudo.titulo}' ({status}).")
        return rep

    def exibir_historico(self) -> None:
        print(f"\n  Histórico de {self.nome}:")
        if not self.historico:
            print("    (vazio)")
            return
        for rep in self.historico:
            status = "concluído" if rep.concluido else f"{rep.progresso_pct:.0f}%"
            print(f"    • {rep.conteudo.titulo:35s} perfil={rep.perfil.nome:10s} {status}")

    def __repr__(self):
        return f"Usuario({self.nome!r}, {self.assinatura.plano.value})"


# ─────────────────────────────────────────
# CatalogoService (dependência)
# ─────────────────────────────────────────

class CatalogoService:
    """
    Dependência de Usuario no diagrama.
    Responsável por busca e filtragem do catálogo.
    """

    def __init__(self):
        self._catalogo: dict[str, Conteudo] = {}

    def adicionar(self, conteudo: Conteudo) -> None:
        self._catalogo[conteudo.id] = conteudo

    def buscar(self, termo: str) -> list[Conteudo]:
        termo_lower = termo.lower()
        return [
            c for c in self._catalogo.values()
            if termo_lower in c.titulo.lower() or termo_lower in c.genero.lower()
        ]

    def listar(self) -> None:
        print(f"\n  Catálogo ({len(self._catalogo)} títulos):")
        for c in self._catalogo.values():
            tipo = "Filme" if isinstance(c, Filme) else f"Série ({c.total_episodios} eps)"
            nota = f"★ {c.nota_media}" if c.nota_media else "sem avaliação"
            print(f"    [{c.id}] {c.titulo:35s} {tipo:20s} {nota}")


# ─────────────────────────────────────────
# DEMONSTRAÇÃO
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== Sistema de Streaming — Netflix ===\n")

    catalogo = CatalogoService()

    # Conteúdo
    f1 = Filme("M001", "Oppenheimer",          "Drama/História", "14", 2023, 180, "Christopher Nolan")
    f2 = Filme("M002", "Interstellar",          "Ficção Científica", "12", 2014, 169, "Christopher Nolan")
    s1 = Serie("S001", "Breaking Bad",          "Drama/Crime",    "18", 2008)
    s2 = Serie("S002", "Stranger Things",       "Ficção/Terror",  "14", 2016)

    for ep_dados in [(1, "Piloto", 58), (2, "Cat's in the Bag", 48), (3, "...And the Bag's in the River", 47)]:
        s1.adicionar_episodio(1, Episodio(*ep_dados))

    for ep_dados in [(1, "O Mundo Virado", 47), (2, "A Promessa", 55)]:
        s2.adicionar_episodio(1, Episodio(*ep_dados))

    for conteudo in [f1, f2, s1, s2]:
        catalogo.adicionar(conteudo)

    # Avaliações
    f2.avaliar(4.9)
    f2.avaliar(5.0)
    s1.avaliar(5.0)
    s1.avaliar(4.8)

    catalogo.listar()

    # Usuário com perfis e assinatura Premium
    print("\n--- Criando usuário ---")
    usuario = Usuario("U001", "Ana Lima", "ana@email.com", PlanoAssinatura.PREMIUM)
    print(f"  {usuario.assinatura}")

    usuario.adicionar_perfil(Perfil("Ana", "avatar_ana", "18"))
    usuario.adicionar_perfil(Perfil("Kids", "avatar_kids", "10"))

    # Reproduções
    print("\n--- Reproduções ---")
    perfil_ana  = usuario.perfis[0]
    perfil_kids = usuario.perfis[1]

    usuario.reproduzir(f2, perfil_ana, 100.0)   # concluído
    usuario.reproduzir(s1, perfil_ana, 45.0)    # em andamento
    usuario.reproduzir(s2, perfil_kids, 60.0)   # em andamento

    # Busca
    print("\n--- Busca no catálogo ---")
    resultados = catalogo.buscar("nolan")
    print(f"  Resultados para 'nolan': {[c.titulo for c in resultados]}")

    # Histórico e duração
    usuario.exibir_historico()

    print(f"\n  Duração total Breaking Bad: {s1.duracao_total_min()} min  "
          f"({s1.total_episodios} episódios)")
    print(f"  Duração total Oppenheimer: {f1.duracao_total_min()} min")
