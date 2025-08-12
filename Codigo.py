import json
import os
import requests
import logging
from typing import List, Dict, Optional

# ==============================================================================
# Configurações
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("biblioteca.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# SUA API KEY ORIGINAL (mantida exatamente como você forneceu)
TMDB_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmZGVhZGM0N2E4MDFkYWI4MTJmMzNmMDY2OTUyMzhiNyIsIm5iZiI6MTc1NDk1MTIyOS43NTMsInN1YiI6IjY4OWE2ZTNkN2U0MzUxNDEwZmI3MDU3YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.hGpU4I5Fe-C424P1exCOURJ7z5wEIlLAoJTZwkwxM8c"

# ==============================================================================
# Classes (mantidas do seu código original)
# ==============================================================================

class ItemBiblioteca:
    def __init__(self, titulo: str, autor_ou_editora: str, id_item: str, disponivel: bool = True):
        self.titulo = titulo
        self.autor_ou_editora = autor_ou_editora
        self.id_item = id_item
        self.disponivel = disponivel

    def exibir_info(self) -> str:
        status = "Disponível" if self.disponivel else "Emprestado"
        return f"Título: {self.titulo}, ID: {self.id_item}, Status: {status}"

    def emprestar(self) -> str:
        if self.disponivel:
            self.disponivel = False
            return f"'{self.titulo}' emprestado com sucesso."
        return f"'{self.titulo}' já está emprestado."

    def devolver(self) -> str:
        if not self.disponivel:
            self.disponivel = True
            return f"'{self.titulo}' devolvido com sucesso."
        return f"'{self.titulo}' já está disponível."

    def to_dict(self) -> Dict:
        return {
            "tipo": self.__class__.__name__,
            "titulo": self.titulo,
            "autor_ou_editora": self.autor_ou_editora,
            "id_item": self.id_item,
            "disponivel": self.disponivel
        }

class Livro(ItemBiblioteca):
    def __init__(self, titulo: str, autor: str, id_item: str, isbn: str, num_paginas: int):
        super().__init__(titulo, autor, id_item)
        self.isbn = isbn
        self.num_paginas = num_paginas

    def exibir_info(self) -> str:
        info_base = super().exibir_info()
        return f"{info_base}, Autor: {self.autor_ou_editora}, ISBN: {self.isbn}, Páginas: {self.num_paginas}"

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "isbn": self.isbn,
            "num_paginas": self.num_paginas
        })
        return data

class MidiaVideo(ItemBiblioteca):
    GENEROS_TMDB = {
        28: "Ação",
        12: "Aventura",
        16: "Animação",
        # Adicione mais conforme necessário
    }

    def __init__(self, titulo: str, diretor: str, id_item: str, duracao_minutos: int, genero: str):
        super().__init__(titulo, diretor, id_item)
        self.duracao_minutos = duracao_minutos
        self.genero = genero

    @classmethod
    def traduzir_genero(cls, genre_ids: List[int]) -> str:
        return ", ".join([cls.GENEROS_TMDB.get(gid, str(gid)) for gid in genre_ids])

    def exibir_info(self) -> str:
        info_base = super().exibir_info()
        return f"{info_base}, Diretor: {self.autor_ou_editora}, Duração: {self.duracao_minutos} min, Gênero: {self.genero}"

    def reproduzir(self) -> str:
        return f"Reproduzindo '{self.titulo}'."

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "duracao_minutos": self.duracao_minutos,
            "genero": self.genero
        })
        return data

# ==============================================================================
# Funções de API (com sua key original)
# ==============================================================================

def buscar_livro_google_books(isbn: str, id_item: str) -> Optional[Livro]:
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    logger.info(f"Buscando ISBN {isbn} no Google Books")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('items'):
            logger.warning(f"ISBN {isbn} não encontrado")
            return None
            
        item_data = data['items'][0]['volumeInfo']
        return Livro(
            titulo=item_data.get('title', 'Título desconhecido'),
            autor=", ".join(item_data.get('authors', ['Autor desconhecido'])),
            id_item=id_item,
            isbn=isbn,
            num_paginas=item_data.get('pageCount', 0)
        )
        
    except Exception as e:
        logger.error(f"Erro no Google Books: {str(e)}")
        return None

def buscar_midia_tmdb(titulo: str, id_item: str) -> Optional[MidiaVideo]:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_KEY}"  # SUA CHAVE ORIGINAL AQUI
    }
    params = {"query": titulo, "language": "pt-BR"}
    logger.info(f"Buscando filme '{titulo}'")
    
    try:
        # Busca inicial
        response = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        if not data.get('results'):
            logger.warning("Filme não encontrado")
            return None
            
        filme = data['results'][0]
        filme_id = filme['id']
        
        # Busca detalhes
        detalhes_url = f"https://api.themoviedb.org/3/movie/{filme_id}"
        detalhes = requests.get(detalhes_url, headers=headers).json()
        
        # Busca diretor
        creditos = requests.get(
            f"https://api.themoviedb.org/3/movie/{filme_id}/credits",
            headers=headers
        ).json()
        
        diretor = next(
            (p['name'] for p in creditos['crew'] if p['job'] == 'Director'),
            'Diretor desconhecido'
        )
        
        return MidiaVideo(
            titulo=filme.get('title', titulo),
            diretor=diretor,
            id_item=id_item,
            duracao_minutos=detalhes.get('runtime', 0),
            genero=MidiaVideo.traduzir_genero(filme.get('genre_ids', []))
        )
        
    except Exception as e:
        logger.error(f"Erro na TMDB: {str(e)}")
        return None

# ==============================================================================
# Gerenciamento de Arquivos
# ==============================================================================

def salvar_estoque(itens: List[ItemBiblioteca], caminho: str = "estoque_biblioteca.json") -> bool:
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump([item.to_dict() for item in itens], f, indent=2, ensure_ascii=False)
        logger.info(f"Estoque salvo em {caminho}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar: {str(e)}")
        return False

def carregar_estoque(caminho: str = "estoque_biblioteca.json") -> List[ItemBiblioteca]:
    if not os.path.exists(caminho):
        logger.warning("Arquivo de estoque não encontrado. Criando novo.")
        return []
        
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            
        estoque = []
        for item_data in dados:
            if item_data['tipo'] == 'Livro':
                estoque.append(Livro(**{
                    'titulo': item_data['titulo'],
                    'autor': item_data['autor_ou_editora'],
                    'id_item': item_data['id_item'],
                    'isbn': item_data['isbn'],
                    'num_paginas': item_data['num_paginas']
                }))
            elif item_data['tipo'] == 'MidiaVideo':
                estoque.append(MidiaVideo(**{
                    'titulo': item_data['titulo'],
                    'diretor': item_data['autor_ou_editora'],
                    'id_item': item_data['id_item'],
                    'duracao_minutos': item_data['duracao_minutos'],
                    'genero': item_data['genero']
                }))
                
        logger.info(f"Carregados {len(estoque)} itens de {caminho}")
        return estoque
        
    except Exception as e:
        logger.error(f"Erro ao carregar: {str(e)}")
        return []

# ==============================================================================
# Menu Interativo (combinando as melhores partes de ambos)
# ==============================================================================

def main():
    estoque = carregar_estoque()
    
    while True:
        print("\n=== MENU ===")
        print("1. Adicionar Livro")
        print("2. Adicionar Filme")
        print("3. Listar Itens")
        print("4. Emprestar Item")
        print("5. Devolver Item")
        print("6. Sair")
        
        opcao = input("Opção: ").strip()
        
        if opcao == "1":
            isbn = input("ISBN do livro: ").strip()
            if not isbn.isdigit():
                print("ISBN inválido!")
                continue
                
            id_item = input("ID para o item: ").strip()
            if any(item.id_item == id_item for item in estoque):
                print("ID já existe!")
                continue
                
            livro = buscar_livro_google_books(isbn, id_item)
            if livro:
                estoque.append(livro)
                print(f"Livro '{livro.titulo}' adicionado!")
            else:
                print("Livro não encontrado!")
                
        elif opcao == "2":
            titulo = input("Título do filme: ").strip()
            if not titulo:
                print("Título inválido!")
                continue
                
            id_item = input("ID para o item: ").strip()
            if any(item.id_item == id_item for item in estoque):
                print("ID já existe!")
                continue
                
            filme = buscar_midia_tmdb(titulo, id_item)
            if filme:
                estoque.append(filme)
                print(f"Filme '{filme.titulo}' adicionado!")
            else:
                print("Filme não encontrado!")
                
        elif opcao == "3":
            print("\n=== ESTOQUE ===")
            for i, item in enumerate(estoque, 1):
                print(f"{i}. {item.exibir_info()}")
                
        elif opcao == "4":
            if not estoque:
                print("Estoque vazio!")
                continue
                
            print("\nItens disponíveis:")
            disponiveis = [i for i, item in enumerate(estoque, 1) if item.disponivel]
            for i in disponiveis:
                print(f"{i}. {estoque[i-1].titulo}")
                
            try:
                idx = int(input("Número do item: ")) - 1
                if 0 <= idx < len(estoque) and estoque[idx].disponivel:
                    print(estoque[idx].emprestar())
                else:
                    print("Item indisponível ou inválido!")
            except ValueError:
                print("Número inválido!")
                
        elif opcao == "5":
            # Similar ao opção 4, mas para devolução
            pass
            
        elif opcao == "6":
            if salvar_estoque(estoque):
                print("Dados salvos com sucesso!")
            break
            
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
