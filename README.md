# Segurança de Prompts em Modelos de LLMs

Este repositório contém o planejamento, a implementação e a pesquisa para um projeto focado na **Segurança de Prompts em Modelos de Linguagem de Grande Escala (LLMs)**. O objetivo principal é desenvolver uma arquitetura robusta que proteja as interações com LLMs contra ataques, como injeção de prompt.

-----

## 🏛️ Arquitetura

O sistema implementa uma arquitetura de microsserviços projetada para interceptar e analisar as requisições do usuário antes e depois de serem processadas pelo LLM. O fluxo é centralizado por um **Orquestrador**, que coordena a comunicação entre os diferentes componentes de segurança.

A arquitetura é composta pelas seguintes entidades:

  * **Usuário:** A entidade que envia o prompt inicial.
  * **Orquestrador:** O cérebro do sistema. Ele recebe o prompt do usuário, o encaminha para o `Sanitizador` para validação, envia o prompt limpo ao LLM e, por fim, passa a resposta do LLM para o `Output Guardrail` antes de devolvê-la ao usuário.
  * **Sanitizador (Sanitizer):** Um microsserviço responsável por analisar o prompt de entrada do usuário. Sua função é detectar e neutralizar potenciais ameaças, como injeções de prompt ou conteúdo malicioso.
  * **Serviço de LLM:** O modelo de linguagem (ex: API da OpenAI) que recebe o prompt sanitizado e gera a resposta.
  * **Output Guardrail:** Um microsserviço que filtra a saída do LLM. Ele garante que a resposta gerada pelo modelo seja segura, apropriada e não contenha informações confidenciais antes de ser exibida ao usuário.

-----

## 📁 Estrutura do Repositório

O projeto está organizado nas seguintes pastas principais:

```
/
├── 📄 sections/
│   └── (Artigo científico do projeto em formato LaTeX)
│
├── 💻 code/
│   ├── orchestrator/     (Microsserviço do Orquestrador) 
│   ├── sanitizer/        (Microsserviço do Sanitizador) 
│   └── guardrail/        (Microsserviço do Output Guardrail) 
│
├── 📊 activity/
│   └── (Slides e materiais de apresentação do projeto)
│
└── README.md
```

-----

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

  * **Linguagem:** Python 
  * **Framework API:** FastAPI & Uvicorn 
  * **Contêineres:** Docker 
  * **LLM:** API da OpenAI 
  * **Diagramação:** Draw.io 

-----

## 🚀 Executando o Projeto

A arquitetura de microsserviços é gerenciada com Docker Compose, facilitando a configuração e execução do ambiente.

1.  **Pré-requisito:** Tenha o Docker e o Docker Compose instalados em sua máquina.
2.  **Navegue até a pasta `code/`:**
    ```bash
    cd code
    ```
3.  **Construa e inicie os serviços:**
    ```bash
    docker-compose up --build
    ```
4.  Isso iniciará os três serviços principais em contêineres separados, conforme definido no `docker-compose.yml`:
      * `sanitizer_service` (porta: 8000) 
      * `orchestrator_service` (porta: 7000) 
      * `output_guardrail_service` (porta: 6000) 

-----

Aqui está uma versão **bem mais resumida**, direta e adequada para o README:

---

# 🧪 Como Executar os Testes

## 1. Testes Unitários

Cada microsserviço possui seus próprios testes.
Execute dentro de cada pasta:

**Sanitizer**

```bash
cd code/sanitizer
pytest -v
```

**Guardrail**

```bash
cd code/guardrail
pytest -v
```

**Orchestrator**

```bash
cd code/orchestrator
pytest -v
```

**Resultados esperados:**

* Sanitizer: 11/11 testes aprovados
* Guardrail: 22/22 aprovados
* Orchestrator: 11/12 aprovados 
---

## 2. Testes de Integração (API)

1. Inicie todos os serviços:

```bash
cd code
docker-compose up --build
```

2. Rode os testes de integração:

```bash
cd code/orchestrator
pytest -v -m integration
```

**Resultado esperado:** 17/17 testes aprovados (100%) 

---

## 3. Testes no Postman

1. Com a arquitetura rodando via Docker
2. Importe a coleção de testes
3. Rode via *Collection Runner*

**Comportamentos esperados:**

* Bloqueio de viés → 400
* Bloqueio de delírios → 400
* Sanitização de dados sensíveis → 200 (texto limpo)
  (Evidências: páginas 11–13 do relatório )

---

## 👥 Equipe

Este projeto foi desenvolvido pelo grupo "Segurança de prompts em modelos de LLMS", composto por:

  * Juan Gustavo 
  * Lucas Emanoel 
  * Lucas Messias
  * Joás Vitor
  * João Victor
