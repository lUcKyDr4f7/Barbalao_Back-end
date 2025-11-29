# API Backend - Barbalão

  

API REST em **Flask** para gerenciamento de barbearia (produtos, categorias e banners).

  

##  Setup

  

### Instalação

```bash

git  clone  https://github.com/Oseias-Augusto/back-end-barbalao.git

cd  back-end-barbalao

python  -m  venv  venv

venv\Scripts\activate  # Windows

pip  install  -r  requirements.txt

python  apiProd.py

```

 
API rodando em `https://back-end-barbalao.onrender.com`

  

---

  

# Endpoints

###  Autenticação

| Método | Endpoint | Descrição |
|:---:|:---:|:---:|
| `POST` | `/api/login/` | Login com `nome` e `senha` |
| `GET` | `/api/check_session/` | Verifica se está autenticado |

  
---

###  Produtos

| Método | Endpoint | Descrição |
|:---:|:---:|:---:|
| `POST` | `/api/products/` | Criar produto |
| `GET` | `/api/products/` | Listar produtos |
| `POST` | `/api/products/atualizar/<id>/` | Atualizar produto |
| `DELETE` | `/api/products/remove/<id>/` | Remover produto |

  
---

###  Categorias

| Método | Endpoint | Descrição |
|:---:|:---:|:---:|
| `POST` | `/api/categoria/` | Criar categoria/subcategoria |
| `GET` | `/api/categoria/` | Listar subcategorias |
| `GET` | `/api/categoria/principais/` | Listar categorias principais |
| `POST` | `/api/categoria/atualizar/<id>/` | Atualizar categoria |
| `DELETE` | `/api/categoria/remove/<id>/` | Remover categoria |

  ---

###  Banners

| Método | Endpoint | Descrição |
|:---:|:---:|:---:|
| `POST` | `/api/banner/` | Criar banner |
| `GET` | `/api/banner/` | Listar banners |
| `POST` | `/api/banner/atualizar/<id>/` | Atualizar banner |
| `DELETE` | `/api/banner/remove/<id>/` | Remover banner |


---

  

##  Segurança

  
- Sessions: HttpOnly, Secure, SameSite=None

- CORS: Configurado para frontend local e produção

  

---

  

##  Banco de Dados

  

-  `usuario` - Usuários

-  `produto` - Produtos/serviços

-  `categoria` - Categorias hierárquicas

-  `banners` - Banners promocionais

  

**Banco:** PostgreSQL (Render)

  

---

 
##  Dependências

  

```

Flask, Flask-CORS, psycopg2-binary, cryptography

```

  

---

  

##  Nota

As credenciais do banco estão no código. Considere usar variáveis de ambiente.

 
