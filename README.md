Sistema Integrado de Gestão de Frota e Comunicação Corporativa

1.	Introdução
O presente projeto consiste no desenvolvimento de um Sistema Integrado de Gestão de Frota e Comunicação Corporativa, desenvolvido com o objetivo de auxiliar empresas no gerenciamento de sua frota de caminhões e na comunicação interna entre administradores e funcionários.

A plataforma permite que administradores publiquem comunicados e notificações para os funcionários da empresa, centralizando informações importantes em um único ambiente digital. Além disso, o sistema disponibiliza funcionalidades voltadas para o gerenciamento da frota de caminhões, permitindo o cadastro de veículos, criação de rotas e acompanhamento do status das entregas, classificadas como concluídas ou pendentes.

Todos os funcionários possuem acesso à visualização de todas as publicações e de todas as rotas cadastradas no sistema.

2.	Objetivos

Objetivo Geral: Desenvolver um sistema web capaz de integrar a comunicação interna da empresa com o gerenciamento da frota de caminhões.

Objetivos Específicos:
- Permitir o cadastro e autenticação de funcionários.
- Disponibilizar diferentes níveis de acesso para administradores e funcionários.
- Permitir a criação e visualização de publicações e comunicados internos.
- Realizar o cadastro e gerenciamento dos caminhões da frota.
- Permitir o cadastro e gerenciamento de rotas.
- Permitir que todos os funcionários visualizem todas as publicações e rotas cadastradas.
- Armazenar informações de forma segura utilizando o Firebase.
- Simular e planejar a infraestrutura de rede através do Cisco Packet Tracer.
3.	Requisitos Funcionais

RF01 Cadastro de funcionários.
RF02 Login de funcionários.
RF03 Login de administradores.
RF04 Página de perfil dos funcionários.
RF05 Criar publicações.
RF06 Excluir publicações.
RF07 Todos os funcionários visualizam todas as publicações.
RF08 Área de comunicação interna.
RF09 Cadastro de caminhões.
RF10 Armazenamento dos caminhões.
RF11 Criação de rotas.
RF12 Registro de rotas concluídas.
RF13 Registro de rotas pendentes.
RF14 Consulta de rotas.
RF15 Todos os funcionários visualizam todas as rotas.
RF16 Diferenciação entre administrador e funcionário.
RF17 Apenas administradores gerenciam dados.¬
RF18 Funcionários possuem acesso somente para visualização.
4.	Requisitos Não Funcionais

Acessível via navegadores modernos, interface intuitiva, armazenamento Firebase, autenticação obrigatória, integridade dos dados, tempo de resposta adequado, HTML/CSS, simulação de rede no Cisco Packet Tracer, acesso simultâneo e organização visual corporativa.
5.	DER

FUNCIONARIO(id_funcionario, nome, email, cargo, departamento, perfil, criado_em)

PUBLICACAO(id_publicacao, titulo, conteudo, data, id_funcionario)

CAMINHAO(id_caminhao, placa, modelo, motorista)¬

ROTA(id_rota, origem, destino, status, id_caminhao)

Relacionamentos:
FUNCIONARIO (1) ---- (N) PUBLICACAO
CAMINHAO (1) ---- (N) ROTA
6.	Modelo Relacional

FUNCIONARIO(id_funcionario PK, nome, email, cargo, departamento, perfil, criado_em)

PUBLICACAO(id_publicacao PK, titulo, conteudo, data, id_funcionario FK)

CAMINHAO(id_caminhao PK, placa, modelo, motorista)

ROTA(id_rota PK, origem, destino, status, id_caminhao FK)
7.	Casos de Uso

Administrador:
- Login
- Perfil
- Criar e excluir publicações
- Cadastrar caminhões
- Criar rotas
- Visualizar frota

Funcionário:
- Login
- Perfil
- Visualizar publicações
- Visualizar todas as rotas
- Visualizar informações da frota
8.	Fluxo do Sistema

Login -> Autenticação -> Verificação de Perfil

Administrador:
Criar publicações, excluir publicações, cadastrar caminhões, criar rotas e visualizar frota.

Funcionário:
Visualizar todas as publicações, visualizar todas as rotas e acessar perfil.
9.	Tecnologias e Conectividade

Arquitetura cliente-servidor utilizando Flask, Firebase, HTML, CSS e Cisco Packet Tracer. Comunicação via HTTP/HTTPS, TCP/IP e DNS. Rede 192.168.1.0/24 com topologia em estrela.
10.	Segurança




Sistema Integrado de Gestão de Frota e Comunicação Corporativa
Versão organizada por disciplinas para entrega acadêmica.
Banco de Dados
Modelagem do banco de dados utilizando Firebase Firestore.

Entidades:
FUNCIONARIO, PUBLICACAO, CAMINHAO e ROTA.

Relacionamentos:
FUNCIONARIO (1:N) PUBLICACAO
CAMINHAO (1:N) ROTA

Modelo relacional e DER desenvolvidos para o sistema.
Engenharia de Software
Levantamento de requisitos funcionais e não funcionais.
Definição dos atores Administrador e Funcionário.
Elaboração dos casos de uso.
Criação do fluxograma do sistema.
Definição das regras de negócio e controle de acesso.
Linguagem de Programação
Desenvolvimento da lógica do sistema utilizando Python e Flask.

Funcionalidades:
- Login
- Cadastro de funcionários
- Publicações
- Cadastro de caminhões
- Cadastro de rotas
- Consulta de dados

Desenvolvimento Web
Interface desenvolvida com HTML5 e CSS3.

Telas:
- Login
- Perfil
- Publicações
- Caminhões
- Rotas

Características:
- Interface intuitiva
- Layout corporativo
- Navegação simples

Tecnologia da Informação e Conectividade (Redes)
Topologia em estrela.

Equipamentos:
- Router Cisco 2911
- Switch Cisco 2960
- Servidor Flask
- Estações de trabalho

Protocolos:
HTTP, HTTPS, TCP/IP e DNS.

Rede utilizada:
192.168.1.0/24

HTTPS, autenticação por login e senha, controle de acesso por perfis, proteção do Firebase, validação de dados e restrição das funcionalidades administrativas. Funcionários possuem acesso de leitura para todas as publicações e rotas.
