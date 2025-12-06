# 🧪 Como Rodar Testes nos Containers

Guia simples para rodar testes dentro de cada container Docker.

---

## 📋 Pré-requisito

Docker Desktop instalado e rodando.

---

## 🚀 Passo a Passo

### **1. Subir os containers**

```bash
cd code
docker-compose up -d
```

Aguarde alguns segundos até todos os containers subirem.

---

### **2. Testar o Sanitizer**

**Acessar o bash do container:**
```bash
docker exec -it sanitizer_service bash
```

**Dentro do container, rodar os testes:**
```bash
python -m pytest tests/ -v
```

**Sair do container:**
```bash
exit
```

---

### **3. Testar o Guardrail**

**Acessar o bash do container:**
```bash
docker exec -it output_guardrail_service bash
```

**Dentro do container, rodar os testes:**
```bash
python -m pytest tests/ -v
```

**Sair do container:**
```bash
exit
```

---

### **4. Testar o Orchestrator**

**Acessar o bash do container:**
```bash
docker exec -it orchestrator_service bash
```

**Dentro do container, rodar os testes:**
```bash
python -m pytest tests/ -v
```

**Sair do container:**
```bash
exit
```

---

### **5. Parar os containers (quando terminar)**

```bash
docker-compose down
```

---

## 📊 O que você vai ver

Quando rodar `python -m pytest tests/ -v`, verá algo assim:

```
==================== test session starts ====================
platform linux -- Python 3.10.x, pytest-x.x.x
rootdir: /app
collected 20 items

tests/test_sanitizer.py::TestNormalizer::test_normalize_removes_invisible_characters PASSED [ 5%]
tests/test_sanitizer.py::TestNormalizer::test_normalize_removes_multiple_invisible_chars PASSED [10%]
tests/test_sanitizer.py::TestNormalizer::test_normalize_limits_length_to_3000 PASSED [15%]
...

==================== 20 passed in 0.23s =====================
```

- ✅ **PASSED** = Teste passou (tudo certo)
- ❌ **FAILED** = Teste falhou (algo errou)

---

## 🔧 Comandos Úteis Dentro do Container

Depois de entrar no bash do container com `docker exec -it <container> bash`:

```bash
# Ver arquivos
ls

# Ver conteúdo da pasta tests
ls tests/

# Rodar testes com mais detalhes
python -m pytest tests/ -vv

# Listar todos os testes sem rodar
python -m pytest tests/ --collect-only

# Rodar um teste específico
python -m pytest tests/test_sanitizer.py::TestNormalizer::test_normalize_removes_invisible_characters

# Parar no primeiro erro
python -m pytest tests/ -x

# Ver prints do código durante os testes
python -m pytest tests/ -s
```

---

## 📦 Resumo de Cada Container

### 🧹 Sanitizer (20 testes)
- Remove caracteres invisíveis
- Limita tamanho do texto (3000 caracteres)
- Normaliza Unicode
- Detecta padrões suspeitos

### 🛡️ Guardrail (15 testes)
- Detecta prompt injection
- Detecta palavras proibidas
- Remove emails e CPFs automaticamente

### 🎭 Orchestrator (11 testes)
- Valida modelos de dados
- Verifica configuração de URLs
- Testa estrutura dos endpoints

**Total: 46 testes**

---

## ⚠️ Problemas Comuns

### ❌ Erro: "Cannot connect to the Docker daemon"
**Solução:** Abra o Docker Desktop e aguarde iniciar.

### ❌ Erro: "No such container"
**Solução:** Os containers não estão rodando. Execute:
```bash
cd code
docker-compose up -d
```

### ❌ Erro: "Error response from daemon: Container is not running"
**Solução:** Suba os containers primeiro:
```bash
docker-compose up -d
```

### ❌ Testes dão erro ao rodar
**Solução:** Reconstrua as imagens:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🎯 Fluxo Completo - Exemplo

```bash
# 1. Subir containers
cd code
docker-compose up -d

# 2. Testar Sanitizer
docker exec -it sanitizer_service bash
python -m pytest tests/ -v
exit

# 3. Testar Guardrail
docker exec -it output_guardrail_service bash
python -m pytest tests/ -v
exit

# 4. Testar Orchestrator
docker exec -it orchestrator_service bash
python -m pytest tests/ -v
exit

# 5. Parar containers
docker-compose down
```

---

## 💡 Dica

Se não quiser entrar no bash, pode rodar direto:

```bash
docker exec sanitizer_service python -m pytest tests/ -v
docker exec output_guardrail_service python -m pytest tests/ -v
docker exec orchestrator_service python -m pytest tests/ -v
```

Isso executa os testes e mostra o resultado sem entrar no container.

---

**Pronto! 🚀**
