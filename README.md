# 📚 Media Hub — Backend Library Management System

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/Architecture-OOP--Polymorphism-orange.svg)]()
[![Integrations](https://img.shields.io/badge/Integrations-REST%20APIs-green.svg)]()

Um sistema robusto de gerenciamento e inventário de mídias (livros e vídeos) desenvolvido em **Python CLI**. O principal diferencial do projeto é o enriquecimento automático de metadados, que elimina o cadastro manual consultando APIs globais em tempo real através do identificador do item (ISBN para livros e título para filmes).

---

## 🎯 Engenharia de Software e Destaques Técnicos

Este projeto foi construído seguindo rigorosos padrões de arquitetura de software, demonstrando proficiência em conceitos de nível intermediário/avançado:

*   **Abstração e Polimorfismo Computacional:** Criação de uma classe abstrata/base (`ItemBiblioteca`) herdada por classes filhas especializadas (`Livro` e `MidiaVideo`). O polimorfismo é aplicado no método `exibir_info()` e na serialização, onde o comportamento adapta-se dinamicamente ao tipo de objeto em tempo de execução.
*   **Consumo Assíncrono e Integração com APIs REST:** Implementação de conectores HTTP utilizando a biblioteca `requests` para comunicação com os serviços **Google Books API** e **TheMovieDB (TMDB) API**, tratando payloads complexos em JSON.
*   **Tratamento de Erros e UX Defensiva:** Controle estrito de fluxos alternativos e falhas de rede através de blocos `try-except-finally` genéricos e específicos (`raise_for_status`), garantindo a resiliência do sistema mesmo em cenários de timeout ou indisponibilidade de serviços externos.
*   **Persistência de Dados e Serialização:** Motor de persistência local implementado via serialização de dicionários em arquivos JSON (`json.dump` / `json.load`), incluindo tratamento nativo de codificação de caracteres (`utf-8`).
*   **Logs Estruturados:** Substituição de comandos `print` na camada de infraestrutura pelo módulo nativo `logging`, registrando eventos simultaneamente em um arquivo físico (`biblioteca.log`) e no console, facilitando a depuração e auditoria do sistema.

---

## 🛠️ Stack Tecnológica

*   **Linguagem:** Python 3.9+
*   **Typing:** Uso sistemático de *Type Hints* (`List`, `Dict`, `Optional`) para garantir a manutenibilidade, legibilidade e suporte a linters estáticos (como o MyPy).
*   **Bibliotecas Nativas:** `json`, `os`, `logging`, `typing`.
*   **Dependências Externas:** `requests` para requisições HTTP.

---

## 📐 Fluxo de Dados e Funcionamento

1.  **Input Mínimo:** O usuário fornece apenas o ISBN de um livro ou o nome de um filme no terminal.
2.  **Enriquecimento (Data Enrichment):** O sistema dispara uma requisição REST, localiza a obra correspondente, parseia o JSON de retorno e extrai automaticamente metadados complexos (como autores, número de páginas, diretores e gêneros mapeados).
3.  **Instanciação Dinâmica:** O objeto correspondente é construído na memória com as informações validadas.
4.  **Estado e Persistência:** Operações de empréstimo/devolução alteram o estado interno dos objetos, que são salvos localmente ao encerrar o programa.
