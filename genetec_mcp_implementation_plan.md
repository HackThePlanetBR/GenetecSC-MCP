# Plano de Implementação: Genetec API MCP Server

**Data:** 2025-11-06  
**Linguagem:** Python com FastMCP  
**Escopo:** Grupos 1 e 2 (Core Entity Management + Access Control Operations)

---

## 📋 Executive Summary

### Decisões Chave
- **Linguagem:** Python 3.10+ com FastMCP
- **Nome do servidor:** `genetec_mcp`
- **Transporte:** stdio (para integração local com Claude Desktop)
- **Autenticação:** HTTP Basic (via variáveis de ambiente)
- **Formato de resposta:** Markdown (default) e JSON (opcional)
- **Limite de caracteres:** 25,000 caracteres
- **Paginação:** Suporte a limit/offset

### Escopo da Implementação
- **Grupo 1:** 6 ferramentas de Entity Management (ALTA prioridade)
- **Grupo 2:** 4 ferramentas de Access Control (ALTA prioridade)
- **Total:** 10 ferramentas essenciais

---

## 🛠️ Arquitetura do Projeto

### Estrutura de Diretórios
```
genetec_mcp/
├── pyproject.toml
├── README.md
├── .env.example
└── src/
    └── genetec_mcp/
        ├── __init__.py
        ├── __main__.py
        ├── server.py          # Servidor FastMCP principal
        ├── config.py          # Configuração e constantes
        ├── models.py          # Modelos Pydantic de entrada
        ├── client.py          # Cliente HTTP para API Genetec
        └── formatters.py      # Funções de formatação de resposta
```

### Dependências (pyproject.toml)
```toml
[project]
name = "genetec-mcp"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.1.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0"
]
```

---

## 🔧 Configuração e Autenticação

### Variáveis de Ambiente (.env)
```bash
GENETEC_SERVER_URL=https://servidor:4590/WebSdk
GENETEC_USERNAME=admin
GENETEC_PASSWORD=senha123
GENETEC_APP_ID=KxsD11z743Hf5Gq9mv3+5ekxzemlCiUXkTFY5ba1NOGcLCmGstt2n0zYE9NsNimv
GENETEC_TIMEOUT=30
```

### Constantes (config.py)
```python
CHARACTER_LIMIT = 25000
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
API_TIMEOUT = 30.0
```

---

## 🛠️ Grupo 1: Core Entity Management (6 ferramentas)

Ferramentas completas e implementadas. Veja FASE_2_COMPLETA.md para detalhes.

---

## 🔐 Grupo 2: Access Control Operations (4 ferramentas)

### Ferramentas Pendentes

1. **genetec_grant_door_access** - Conceder acesso temporário
2. **genetec_lock_unlock_door** - Travar/destravar porta
3. **genetec_list_access_events** - Listar eventos de acesso
4. **genetec_create_visitor** - Criar visitante temporário

Veja documentação completa para especificações detalhadas.

---

## 📚 Referências

- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Genetec API Manual](api-manual.md)

---

**Status:** 🚀 Fase 2 Completa (6/10 ferramentas)  
**Próximo:** ⏳ Fase 3 (Grupo 2 - Access Control)
