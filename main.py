from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title = "API de Livros",
    description = "Catálogo de Livros",
    version = "0.0.1",
    contact ={"name":"Igor Araujo",
              "email":"igormoser@outlook.com"})

lista_livros = {}
tarefas: List[Tarefa] = []

class Tarefa(BaseModel):
    nome: str
    descricao: str
    concluida: Optional[bool] = False

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

@app.get("/tarefas")
def listar_tarefas():
    return tarefas

@app.get("/livros")
def get_livros():
    if not lista_livros:
        return {"Este livro não existe na lista!"}
    else:
        return {"Livros": lista_livros}
@app.post("/tarefas")
def adicionar_tarefas(tarefa: Tarefa):
    tarefas.append(tarefa)
    return {"mensagem": "Tarefa adicionada com sucesso!", "tarefa": tarefa}

@app.post("/adicionar")
def post_livros(id_livro: int, livro: Livro):
    if id_livro in lista_livros:
        raise HTTPException(status_code=400, detail="Este livro já existe na lista!")
    else:
        lista_livros[id_livro] = livro.model_dump()
        return {"message": "O livro foi adicionado com sucesso!"}
@app.put("/tarefas/{nome}")
def concluir_tarefa(nome: str):
    for tarefa in tarefas:
        if tarefa.nome == nome:
            tarefa.concluida = True
            return {"mensagem":"Tarefa concluida com sucesso!", "tarefa": tarefa}
    return {"Erro": "Tarefa não encontrada!"}


@app.put("/atualizar/{id_livro}")
def put_livros(id_livro: int, livro: Livro):
    meu_livro = lista_livros.get(id_livro)
    if not meu_livro:
        raise HTTPException(status_code=404, detail="Este livro não foi encontrado!")
    else:
        lista_livros[id_livro] = livro.model_dump()
        return {"message": "O livro foi atualizado com sucesso!"}
@app.delete("/tarefas/{nome}")
def remover_tarefas(nome: str):
    for tarefa in tarefas:
        if tarefa.nome == nome:
            tarefa.remove(tarefa)
            return {"message": "Tarefa removida com sucesso!", "tarefa": tarefa}
    return {"Erro": "Tarefa não encontrada"}

 @app.delete("/deletar/{id_livro}")
def delete_livros(id_livro: int):
    if id_livro not in lista_livros:
        raise HTTPException(status_code=404, detail="Este livro não foi encontrado!")
    else:
        del lista_livros[id_livro]
        return {"message": "O livro foi deletado!"}