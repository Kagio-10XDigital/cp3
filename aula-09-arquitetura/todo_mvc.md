# To-Do List MVC — Diagrama de Arquitetura

## Visão geral

Este documento descreve a arquitetura MVC da aplicação To-Do List e complementa
as imagens `todo_mvc.png` (diagrama) e `telas-figma.png` (protótipo).

## Estrutura MVC

```
┌─────────────────────────────────────────────────────────────┐
│                        VIEW (Interface)                     │
│   ┌──────────────────┐       ┌──────────────────────────┐   │
│   │  ListaTasksView  │       │   FormularioTaskView     │   │
│   │  - exibir lista  │       │   - campo título         │   │
│   │  - marcar feito  │       │   - campo descrição      │   │
│   │  - botão excluir │       │   - botão salvar         │   │
│   └────────┬─────────┘       └───────────┬──────────────┘   │
└────────────│─────────────────────────────│──────────────────┘
             │ eventos                     │ eventos
             ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    CONTROLLER (Lógica)                      │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  TaskController                     │   │
│   │   + adicionar_task(titulo, descricao)               │   │
│   │   + concluir_task(id)                               │   │
│   │   + excluir_task(id)                                │   │
│   │   + listar_tasks() → lista filtrada                 │   │
│   └────────────────────────┬────────────────────────────┘   │
└────────────────────────────│────────────────────────────────┘
                             │ CRUD
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      MODEL (Dados)                          │
│   ┌────────────────────┐   ┌───────────────────────────┐    │
│   │       Task         │   │       TaskRepository      │    │
│   │  - id              │   │  - tasks: list[Task]      │    │
│   │  - titulo          │   │  + salvar(task)           │    │
│   │  - descricao       │   │  + buscar(id)             │    │
│   │  - concluida       │   │  + listar()               │    │
│   │  - criada_em       │   │  + excluir(id)            │    │
│   └────────────────────┘   └───────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Responsabilidades

| Camada     | Classe               | Responsabilidade                    |
| ---------- | -------------------- | ----------------------------------- |
| Model      | `Task`               | Dados e estado de uma tarefa        |
| Model      | `TaskRepository`     | Persistência e consulta das tarefas |
| Controller | `TaskController`     | Regras de negócio e orquestração    |
| View       | `ListaTasksView`     | Exibe lista e botões de ação        |
| View       | `FormularioTaskView` | Formulário de criação de tarefa     |

## Fluxo de dados

1. Usuário interage com a **View** (ex.: clica em "Adicionar Tarefa")
2. **View** chama método do **Controller** (`adicionar_task(...)`)
3. **Controller** valida e aciona o **Repository** do **Model**
4. **Model** persiste e retorna o estado atualizado
5. **Controller** notifica a **View** para re-renderizar
