"""
SRS do FIAP Marketplace
Aula 04 - Documento SRS (Software Requirements Specification)

Parte 1: Modelagem dos requisitos funcionais e não-funcionais
Parte 2: Validação e simulação do sistema de marketplace
"""

# ─────────────────────────────────────────
# PARTE 1 — Modelagem do SRS
# ─────────────────────────────────────────

SRS = {
    "projeto": "FIAP Marketplace",
    "versao": "1.0",
    "data": "2026-05-20",
    "autores": ["Equipe de Engenharia de Software — FIAP"],

    # RF: o que o sistema DEVE fazer
    "requisitos_funcionais": [
        {
            "id": "RF-01",
            "titulo": "Cadastro de Usuário",
            "descricao": "O sistema deve permitir o cadastro de usuários com nome, e-mail e senha.",
            "prioridade": "Alta",
            "criterio_aceitacao": "Usuário recebe e-mail de confirmação após cadastro bem-sucedido.",
        },
        {
            "id": "RF-02",
            "titulo": "Autenticação",
            "descricao": "O sistema deve autenticar usuários via e-mail e senha.",
            "prioridade": "Alta",
            "criterio_aceitacao": "Login bem-sucedido gera token de sessão válido por 24 h.",
        },
        {
            "id": "RF-03",
            "titulo": "Listagem de Produtos",
            "descricao": "O sistema deve exibir produtos com nome, preço, descrição e estoque.",
            "prioridade": "Alta",
            "criterio_aceitacao": "Listagem atualiza em tempo real quando estoque é alterado.",
        },
        {
            "id": "RF-04",
            "titulo": "Carrinho de Compras",
            "descricao": "O sistema deve permitir adicionar, remover e alterar quantidades no carrinho.",
            "prioridade": "Alta",
            "criterio_aceitacao": "Carrinho persiste entre sessões do mesmo usuário.",
        },
        {
            "id": "RF-05",
            "titulo": "Processamento de Pagamento",
            "descricao": "O sistema deve processar pagamentos via cartão de crédito e PIX.",
            "prioridade": "Alta",
            "criterio_aceitacao": "Pagamento confirmado notifica vendedor e atualiza estoque.",
        },
        {
            "id": "RF-06",
            "titulo": "Gestão de Pedidos",
            "descricao": "Compradores e vendedores devem acompanhar o status dos pedidos.",
            "prioridade": "Média",
            "criterio_aceitacao": "Status muda entre: Aguardando, Pago, Em trânsito, Entregue.",
        },
        {
            "id": "RF-07",
            "titulo": "Avaliação de Vendedores",
            "descricao": "Compradores podem avaliar vendedores com nota de 1 a 5 estrelas.",
            "prioridade": "Baixa",
            "criterio_aceitacao": "Avaliação só é permitida após entrega confirmada.",
        },
    ],

    # RNF: restrições de qualidade, desempenho, segurança
    "requisitos_nao_funcionais": [
        {
            "id": "RNF-01",
            "categoria": "Desempenho",
            "descricao": "O sistema deve responder a 95% das requisições em menos de 2 segundos.",
        },
        {
            "id": "RNF-02",
            "categoria": "Disponibilidade",
            "descricao": "O sistema deve ter disponibilidade de 99,9% (máx. 8,7 h de indisponibilidade/ano).",
        },
        {
            "id": "RNF-03",
            "categoria": "Segurança",
            "descricao": "Senhas devem ser armazenadas com hash bcrypt (salt ≥ 12 rounds).",
        },
        {
            "id": "RNF-04",
            "categoria": "Segurança",
            "descricao": "Toda comunicação deve usar TLS 1.3 ou superior.",
        },
        {
            "id": "RNF-05",
            "categoria": "Escalabilidade",
            "descricao": "A arquitetura deve suportar escalonamento horizontal sem downtime.",
        },
        {
            "id": "RNF-06",
            "categoria": "Usabilidade",
            "descricao": "Interface deve ser responsiva e acessível (WCAG 2.1 nível AA).",
        },
        {
            "id": "RNF-07",
            "categoria": "Manutenibilidade",
            "descricao": "Cobertura de testes automatizados mínima de 80%.",
        },
    ],

    # Stakeholders do sistema
    "stakeholders": [
        {"papel": "Comprador",  "descricao": "Usuário que busca e compra produtos."},
        {"papel": "Vendedor",   "descricao": "Usuário que cadastra e vende produtos."},
        {"papel": "Administrador", "descricao": "Gerencia usuários, produtos e disputas."},
        {"papel": "Sistema de Pagamento", "descricao": "Gateway externo (ex.: Stripe, PagSeguro)."},
    ],
}


# ─────────────────────────────────────────
# PARTE 2 — Simulação do sistema Marketplace
# ─────────────────────────────────────────

class Produto:
    """Representa um produto no marketplace."""

    def __init__(self, id_: str, nome: str, preco: float, estoque: int, vendedor: str):
        if preco <= 0:
            raise ValueError("Preço deve ser positivo.")
        if estoque < 0:
            raise ValueError("Estoque não pode ser negativo.")
        self.id = id_
        self.nome = nome
        self.preco = preco
        self.estoque = estoque
        self.vendedor = vendedor

    def __repr__(self):
        return f"Produto({self.nome}, R${self.preco:.2f}, estoque={self.estoque})"


class Carrinho:
    """Carrinho de compras de um usuário (RF-04)."""

    def __init__(self, usuario: str):
        self.usuario = usuario
        self.itens: dict[str, dict] = {}  # produto_id -> {produto, quantidade}

    def adicionar(self, produto: Produto, quantidade: int = 1) -> None:
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva.")
        if produto.estoque < quantidade:
            raise ValueError(f"Estoque insuficiente para '{produto.nome}'.")

        if produto.id in self.itens:
            self.itens[produto.id]["quantidade"] += quantidade
        else:
            self.itens[produto.id] = {"produto": produto, "quantidade": quantidade}
        print(f"[+] {quantidade}x '{produto.nome}' adicionado ao carrinho.")

    def remover(self, produto_id: str) -> None:
        if produto_id not in self.itens:
            raise KeyError("Produto não encontrado no carrinho.")
        nome = self.itens.pop(produto_id)["produto"].nome
        print(f"[-] '{nome}' removido do carrinho.")

    def total(self) -> float:
        return sum(
            item["produto"].preco * item["quantidade"]
            for item in self.itens.values()
        )

    def exibir(self) -> None:
        print(f"\nCarrinho de {self.usuario}:")
        if not self.itens:
            print("  (vazio)")
            return
        for item in self.itens.values():
            p = item["produto"]
            qtd = item["quantidade"]
            print(f"  • {p.nome:25s} {qtd:2d}x  R${p.preco:.2f} = R${p.preco * qtd:.2f}")
        print(f"  {'Total:':30s} R${self.total():.2f}")


class SistemaMarketplace:
    """Sistema principal do marketplace (RF-01 a RF-06)."""

    METODOS_PAGAMENTO = ["cartao_credito", "pix"]
    STATUS_PEDIDO = ["Aguardando", "Pago", "Em trânsito", "Entregue"]

    def __init__(self):
        self.usuarios: dict[str, str] = {}   # email -> senha (simulado)
        self.produtos: dict[str, Produto] = {}
        self.pedidos: list[dict] = []
        self._proximo_pedido = 1

    # RF-01
    def cadastrar_usuario(self, nome: str, email: str, senha: str) -> None:
        if email in self.usuarios:
            raise ValueError(f"E-mail '{email}' já cadastrado.")
        if len(senha) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres.")
        self.usuarios[email] = senha
        print(f"[OK] Usuário '{nome}' cadastrado com sucesso.")

    # RF-02
    def autenticar(self, email: str, senha: str) -> bool:
        if self.usuarios.get(email) == senha:
            print(f"[OK] Usuário '{email}' autenticado.")
            return True
        print("[ERRO] Credenciais inválidas.")
        return False

    # RF-03
    def cadastrar_produto(self, produto: Produto) -> None:
        self.produtos[produto.id] = produto
        print(f"[OK] Produto '{produto.nome}' cadastrado.")

    def listar_produtos(self) -> None:
        print("\n--- Produtos disponíveis ---")
        for p in self.produtos.values():
            if p.estoque > 0:
                print(f"  [{p.id}] {p.nome:25s} R${p.preco:8.2f}  estoque: {p.estoque}")

    # RF-05
    def finalizar_compra(self, carrinho: Carrinho, metodo: str) -> None:
        if metodo not in self.METODOS_PAGAMENTO:
            raise ValueError(f"Método inválido. Use: {self.METODOS_PAGAMENTO}")
        if not carrinho.itens:
            raise ValueError("Carrinho vazio.")

        # debita estoque
        for item in carrinho.itens.values():
            item["produto"].estoque -= item["quantidade"]

        pedido = {
            "id": f"PED-{self._proximo_pedido:04d}",
            "usuario": carrinho.usuario,
            "itens": list(carrinho.itens.values()),
            "total": carrinho.total(),
            "metodo": metodo,
            "status": "Pago",
        }
        self.pedidos.append(pedido)
        self._proximo_pedido += 1
        carrinho.itens.clear()

        print(f"\n[OK] Pedido {pedido['id']} realizado! "
              f"Total: R${pedido['total']:.2f} via {metodo}.")

    # RF-06
    def atualizar_status(self, pedido_id: str, novo_status: str) -> None:
        if novo_status not in self.STATUS_PEDIDO:
            raise ValueError(f"Status inválido: {self.STATUS_PEDIDO}")
        for p in self.pedidos:
            if p["id"] == pedido_id:
                p["status"] = novo_status
                print(f"[OK] Pedido {pedido_id} atualizado para '{novo_status}'.")
                return
        raise KeyError(f"Pedido '{pedido_id}' não encontrado.")


# ─────────────────────────────────────────
# DEMONSTRAÇÃO
# ─────────────────────────────────────────

def exibir_srs_resumo() -> None:
    """Exibe um resumo do documento SRS."""
    print("=" * 60)
    print(f"  SRS — {SRS['projeto']}  (v{SRS['versao']}  {SRS['data']})")
    print("=" * 60)

    print(f"\nRequisitos Funcionais ({len(SRS['requisitos_funcionais'])}):")
    for rf in SRS["requisitos_funcionais"]:
        print(f"  [{rf['id']}] {rf['titulo']:30s} [{rf['prioridade']}]")

    print(f"\nRequisitos Não-Funcionais ({len(SRS['requisitos_nao_funcionais'])}):")
    for rnf in SRS["requisitos_nao_funcionais"]:
        print(f"  [{rnf['id']}] [{rnf['categoria']:15s}] {rnf['descricao'][:55]}...")

    print(f"\nStakeholders: {', '.join(s['papel'] for s in SRS['stakeholders'])}")
    print("=" * 60)


if __name__ == "__main__":
    # Parte 1: exibe o SRS
    exibir_srs_resumo()

    print("\n\n--- Parte 2: Simulação do Marketplace ---\n")

    mkt = SistemaMarketplace()

    # Cadastro e autenticação
    mkt.cadastrar_usuario("Maria Souza", "maria@fiap.com", "senha123")
    mkt.autenticar("maria@fiap.com", "senha123")
    mkt.autenticar("maria@fiap.com", "errada")

    # Produtos
    p1 = Produto("P001", "Notebook Lenovo IdeaPad", 3299.00, 10, "TechStore")
    p2 = Produto("P002", "Mouse Logitech MX Master", 499.90, 25, "TechStore")
    p3 = Produto("P003", "Teclado Mecânico Keychron", 749.00,  5, "TechStore")

    mkt.cadastrar_produto(p1)
    mkt.cadastrar_produto(p2)
    mkt.cadastrar_produto(p3)
    mkt.listar_produtos()

    # Carrinho e compra
    carrinho = Carrinho("maria@fiap.com")
    carrinho.adicionar(p1, 1)
    carrinho.adicionar(p2, 2)
    carrinho.exibir()

    mkt.finalizar_compra(carrinho, "pix")
    mkt.atualizar_status("PED-0001", "Em trânsito")

    # Listagem após venda
    print()
    mkt.listar_produtos()
