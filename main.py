import secrets
from typing import List
from fastapi import FastAPI, HTTPException, Query
from fastapi.params import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

app = FastAPI(
    title="API de Livros e Tarefas",
    description="Catálogo de Livros e Gerenciamento de Tarefas",
    version="0.0.1",
    contact={"name": "Igor Araujo", "email": "igormoser@outlook.com"},
)

MEU_USUARIO = "admin"
MINHA_SENHA = "admin"
security = HTTPBasic()

class Tarefa(BaseModel):
    nome: str
    descricao: str
    concluida: bool = False

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

def autenticar_meu_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, MEU_USUARIO)
    is_password_correct = secrets.compare_digest(credentials.password, MINHA_SENHA)
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Usuario ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials

lista_livros = {}
tarefas: List[Tarefa] = []

@app.get("/tarefas")
def listar_tarefas(
    page: int = 1,
    size: int = 10,
    sort_by: str = Query(None, regex="^(nome|descricao|concluida)?$"),
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="Página ou tamanho inválidos")
    data = tarefas
    if sort_by:
        data = sorted(data, key=lambda t: getattr(t, sort_by))
    start = (page - 1) * size
    end = start + size
    return {"page": page, "size": size, "total": len(data), "tarefas": data[start:end]}

@app.post("/tarefas")
def adicionar_tarefas(
    tarefa: Tarefa, credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario)
):
    tarefas.append(tarefa)
    return {"mensagem": "Tarefa adicionada com sucesso!", "tarefa": tarefa}

@app.put("/tarefas/{nome}")
def concluir_tarefa(
    nome: str, credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario)
):
    for tarefa in tarefas:
        if tarefa.nome == nome:
            tarefa.concluida = True
            return {"mensagem": "Tarefa concluída com sucesso!", "tarefa": tarefa}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada!")

@app.delete("/tarefas/{nome}")
def remover_tarefas(
    nome: str, credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario)
):
    for tarefa in tarefas:
        if tarefa.nome == nome:
            tarefas.remove(tarefa)
            return {"mensagem": "Tarefa removida com sucesso!", "tarefa": tarefa}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada!")

@app.get("/livros")
def get_livros(
    page: int = 1,
    size: int = 10,
    sort_by: str = Query("id", regex="^(id|nome_livro|autor_livro|ano_livro)$"),
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="Página ou tamanho inválidos")
    if sort_by == "id":
        livros_ordenados = sorted(lista_livros.items(), key=lambda item: item[0])
    else:
        livros_ordenados = sorted(
            lista_livros.items(), key=lambda item: item[1][sort_by]
        )
    start = (page - 1) * size
    end = start + size
    livros_paginados = [
        {"id": id_livro, **livro_data} for id_livro, livro_data in livros_ordenados[start:end]
    ]
    return {
        "page": page,
        "size": size,
        "total": len(lista_livros),
        "livros": livros_paginados,
    }

@app.post("/adicionar")
def post_livros(
    id_livro: int,
    livro: Livro,
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    if id_livro in lista_livros:
        raise HTTPException(status_code=400, detail="Este livro já existe na lista!")
    lista_livros[id_livro] = livro.model_dump()
    return {"mensagem": "O livro foi adicionado com sucesso!"}

@app.put("/atualizar/{id_livro}")
def put_livros(
    id_livro: int,
    livro: Livro,
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario),
):
    if id_livro not in lista_livros:
        raise HTTPException(status_code=404, detail="Este livro não foi encontrado!")
    lista_livros[id_livro] = livro.model_dump()
    return {"mensagem": "O livro foi atualizado com sucesso!"}

@app.delete("/deletar/{id_livro}")
def delete_livros(
    id_livro: int, credentials: HTTPBasicCredentials = Depends(autenticar_meu_usuario)
):
    if id_livro not in lista_livros:
        raise HTTPException(status_code=404, detail="Este livro não foi encontrado!")
    del lista_livros[id_livro]
    return {"mensagem": "O livro foi deletado!"}
