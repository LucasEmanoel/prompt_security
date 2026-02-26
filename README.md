# Segurança de Prompts em Modelos de LLMs

Este repositório contém o planejamento, a implementação e a pesquisa para um projeto focado na **Segurança de Prompts em Modelos de Linguagem de Grande Escala (LLMs)**. O objetivo principal é desenvolver uma arquitetura robusta que proteja as interações com LLMs contra ataques, como injeção de prompt.

-----

## 🏛️ Arquitetura

O sistema implementa uma arquitetura de microsserviços projetada para interceptar e analisar as requisições do usuário antes e depois de serem processadas pelo LLM. O fluxo é centralizado por um **Orquestrador**, que coordena a comunicação entre os diferentes componentes de segurança.

A arquitetura é composta pelas seguintes entidades:

  * **Usuário:** A entidade que envia o prompt inicial.
  * **Orquestrador:** O cérebro do sistema. Ele recebe o prompt do usuário, o encaminha para o `Sanitizador` para validação, envia o prompt limpo ao LLM e, por fim, passa a resposta do LLM para o `Output Guardrail` antes de devolvê-la ao usuário.
  * **Sanitizador (Sanitizer):** Um microsserviço responsável por analisar o prompt de entrada do usuário. Sua função é detectar e neutralizar potenciais ameaças, como injeções de prompt ou conteúdo malicioso.
  * **LLM:** O modelo de linguagem que recebe o prompt sanitizado e gera a resposta.
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
│   └── guardrail/        (Microsserviço do Input Guardrail)
|   └── bias_guardrail/   (Microsserviço do Bias Guardrail)
|   └── output_guardrail/ (Microsserviço do Bias Guardrail)  
|   └── streamlit_app/    (Interface para comunicação com o chat)
|
├── 📊 activity/
│   └── (Slides e materiais de apresentação do projeto)
│
└── README.md
```

-----

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

  * **Linguagem:** Python 
  * **Framework API:** FastAPI, Guardrail Ai & Uvicorn
  * **Interface:** Streamlit
  * **Contêineres:** Docker 
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
      * `guardrail_service` (porta: 6000)
      * `bias_guardrail` (porta: 5000)
      * `output_guardrail` (porta: 4000)
      * `streamlit_service` (porta: 8501)
5.  Abrir o navegador no seguinte endereço:
    ```
    http://localhost:8501
    ```

-----

## 👥 Equipe

Este projeto foi desenvolvido pelo grupo "Segurança de prompts em modelos de LLMS", composto por:

  * Juan Gustavo 
  * Lucas Emanoel 
  * Lucas Messias
  * Joás Vitor
  * João Victor
