"""
GymTrack — Validador de Treino
Aula 03 - Requisitos Funcionais vs. Não-Funcionais

Parte 1: Validação básica de dados de treino
Parte 2: Cálculo de métricas e feedback
Parte 3: Histórico de treinos e relatório
"""

# ─────────────────────────────────────────
# PARTE 1 — Validação básica de dados de treino
# ─────────────────────────────────────────

EXERCICIOS_VALIDOS = [
    "supino", "agachamento", "deadlift", "remada",
    "rosca", "triceps", "leg press", "shoulder press"
]

NIVEIS_VALIDOS = ["iniciante", "intermediario", "avancado"]


def validar_nome(nome: str) -> bool:
    """Verifica se o nome do usuário tem pelo menos 3 caracteres."""
    return isinstance(nome, str) and len(nome.strip()) >= 3


def validar_exercicio(exercicio: str) -> bool:
    """Verifica se o exercício está na lista de exercícios suportados."""
    return exercicio.lower().strip() in EXERCICIOS_VALIDOS


def validar_series_repeticoes(series: int, repeticoes: int) -> bool:
    """Valida que séries estejam entre 1-10 e repetições entre 1-50."""
    return (1 <= series <= 10) and (1 <= repeticoes <= 50)


def validar_peso(peso: float) -> bool:
    """Peso deve ser positivo e no máximo 500 kg."""
    return isinstance(peso, (int, float)) and 0 < peso <= 500


def validar_nivel(nivel: str) -> bool:
    """Verifica se o nível informado é válido."""
    return nivel.lower().strip() in NIVEIS_VALIDOS


def validar_treino(nome: str, exercicio: str, series: int,
                   repeticoes: int, peso: float, nivel: str) -> dict:
    """
    Valida todos os dados de um treino e retorna um relatório de validação.
    Requisito Funcional: sistema deve rejeitar dados inválidos com mensagem clara.
    """
    erros = []

    if not validar_nome(nome):
        erros.append("Nome inválido: mínimo 3 caracteres.")
    if not validar_exercicio(exercicio):
        erros.append(f"Exercício '{exercicio}' não reconhecido. Opções: {EXERCICIOS_VALIDOS}")
    if not validar_series_repeticoes(series, repeticoes):
        erros.append("Séries devem estar entre 1-10 e repetições entre 1-50.")
    if not validar_peso(peso):
        erros.append("Peso inválido: deve ser entre 0.1 e 500 kg.")
    if not validar_nivel(nivel):
        erros.append(f"Nível '{nivel}' inválido. Opções: {NIVEIS_VALIDOS}")

    return {
        "valido": len(erros) == 0,
        "erros": erros
    }


# ─────────────────────────────────────────
# PARTE 2 — Cálculo de métricas e feedback
# ─────────────────────────────────────────

LIMITES_NIVEL = {
    "iniciante":     {"peso_max": 40,  "volume_max": 300},
    "intermediario": {"peso_max": 100, "volume_max": 800},
    "avancado":      {"peso_max": 250, "volume_max": 2000},
}


def calcular_volume(series: int, repeticoes: int, peso: float) -> float:
    """Volume total = séries × repetições × peso (kg)."""
    return series * repeticoes * peso


def calcular_carga_relativa(peso: float, nivel: str) -> float:
    """Percentual do peso em relação ao limite do nível."""
    limite = LIMITES_NIVEL[nivel.lower()]["peso_max"]
    return round((peso / limite) * 100, 1)


def gerar_feedback(series: int, repeticoes: int, peso: float, nivel: str) -> str:
    """
    Gera feedback personalizado baseado no volume e nível do aluno.
    Requisito Não-Funcional: resposta deve ser gerada em < 1 s e ser legível.
    """
    volume = calcular_volume(series, repeticoes, peso)
    volume_max = LIMITES_NIVEL[nivel.lower()]["volume_max"]
    percentual = (volume / volume_max) * 100

    if percentual < 40:
        return "Treino leve — considere aumentar o peso ou o número de séries."
    elif percentual < 70:
        return "Treino moderado — boa intensidade para o seu nível!"
    elif percentual < 90:
        return "Treino intenso — excellent! Monitore a recuperação."
    else:
        return "Treino no limite — certifique-se de descansar adequadamente."


# ─────────────────────────────────────────
# PARTE 3 — Histórico de treinos e relatório
# ─────────────────────────────────────────

historico: list[dict] = []


def registrar_treino(nome: str, exercicio: str, series: int,
                     repeticoes: int, peso: float, nivel: str) -> None:
    """
    Registra um treino no histórico após validação completa.
    Requisito Funcional: sistema deve persistir treinos válidos em memória.
    """
    validacao = validar_treino(nome, exercicio, series, repeticoes, peso, nivel)

    if not validacao["valido"]:
        print("\n[ERRO] Treino rejeitado:")
        for erro in validacao["erros"]:
            print(f"  - {erro}")
        return

    volume = calcular_volume(series, repeticoes, peso)
    feedback = gerar_feedback(series, repeticoes, peso, nivel)

    registro = {
        "nome": nome,
        "exercicio": exercicio,
        "series": series,
        "repeticoes": repeticoes,
        "peso_kg": peso,
        "nivel": nivel,
        "volume_total": volume,
        "feedback": feedback,
    }
    historico.append(registro)
    print(f"\n[OK] Treino registrado para {nome}.")
    print(f"     Volume: {volume:.1f} kg  |  {feedback}")


def exibir_relatorio() -> None:
    """
    Exibe relatório consolidado de todos os treinos registrados.
    Requisito Funcional: sistema deve permitir consulta ao histórico.
    """
    if not historico:
        print("\nNenhum treino registrado ainda.")
        return

    print("\n" + "=" * 55)
    print("          RELATÓRIO DE TREINOS — GymTrack")
    print("=" * 55)

    alunos = {}
    for t in historico:
        alunos.setdefault(t["nome"], []).append(t)

    for aluno, treinos in alunos.items():
        volume_total = sum(t["volume_total"] for t in treinos)
        print(f"\nAluno: {aluno}  |  Treinos: {len(treinos)}  |  Volume acumulado: {volume_total:.1f} kg")
        for t in treinos:
            print(f"  • {t['exercicio'].capitalize():15s} — "
                  f"{t['series']}x{t['repeticoes']} @ {t['peso_kg']} kg")

    print("=" * 55)


# ─────────────────────────────────────────
# DEMONSTRAÇÃO
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== GymTrack — Validador de Treino ===\n")

    # Parte 1: testes de validação
    print("--- Parte 1: Validação ---")
    resultado = validar_treino("Ana Silva", "supino", 4, 12, 50.0, "intermediario")
    print("Treino válido:", resultado["valido"])

    resultado_invalido = validar_treino("Jo", "voar", 0, 60, -5.0, "mestre")
    print("Treino inválido:", resultado_invalido["valido"])
    print("Erros encontrados:", resultado_invalido["erros"])

    # Parte 2: cálculo de métricas
    print("\n--- Parte 2: Métricas ---")
    vol = calcular_volume(4, 12, 50.0)
    print(f"Volume total: {vol} kg")
    carga = calcular_carga_relativa(50.0, "intermediario")
    print(f"Carga relativa: {carga}% do limite do nível")
    print("Feedback:", gerar_feedback(4, 12, 50.0, "intermediario"))

    # Parte 3: histórico e relatório
    print("\n--- Parte 3: Histórico ---")
    registrar_treino("Ana Silva",   "supino",      4, 12, 50.0,  "intermediario")
    registrar_treino("Carlos Lima", "agachamento", 5, 10, 80.0,  "avancado")
    registrar_treino("Ana Silva",   "remada",      3, 15, 35.0,  "intermediario")
    registrar_treino("Jo",          "voar",        0, 60, -5.0,  "mestre")   # inválido

    exibir_relatorio()
