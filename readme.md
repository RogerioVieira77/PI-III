# Agasalho Aqui

![Logo Agasalho Aqui](https://private-us-east-1.manuscdn.com/sessionFile/tdoESe0rdNXl5uwJnENTbB/sandbox/PGupDsxTGD3RTrdfbYY5vs-images_1745382423193_na1fn_L2hvbWUvdWJ1bnR1L3RlbV9hZ2FzYWxob19hcXVpL3N0YXRpYy9pbWFnZXMvSGVhcnRCb3hsb2dv.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvdGRvRVNlMHJkTlhsNXV3Sm5FTlRiQi9zYW5kYm94L1BHdXBEc3hUR0QzUlRyZGZiWVk1dnMtaW1hZ2VzXzE3NDUzODI0MjMxOTNfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzUmxiVjloWjJGellXeG9iMTloY1hWcEwzTjBZWFJwWXk5cGJXRm5aWE12U0dWaGNuUkNiM2hzYjJkdi5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3NjcyMjU2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=XSb0mBXC7OUjWijTqEcEdp7TKs7mNOsU0G0~VNiWCmDBCV3~EuE5NCGIs8YgyVDrU-3TWzS5rjFh9dKECkdjVKfb5P9Pfi2s7~vyTPWELtnLexgzBu5uMoObyusZ2tCLDfEXrpCvlgiDtWHLtBUX2bq6pjUTcTA2HJFvy1E2ZjdMesxxVfUVmg9XOTuzwDIPqJq0kH5Q-xh9D8NkgtW7ytO3P6AeQUf8-uol7tFUk-jbN43JBzss7xKMnIvt6RE0qpFjjO31BUSSO-UhOBOlcWlQmaAfmc1G45XFBQjut2UfnNf7iWe4nWhYQF9j76DmLZOxXLZ6G1-UQen5yoMB5w__)

## Sobre o Projeto

**Agasalho Aqui** é uma plataforma web desenvolvida para conectar doadores de roupas com pontos de coleta. O projeto foi criado por estudantes da Universidade Virtual do Estado de São Paulo (UNIVESP) com o objetivo de facilitar o processo de doação de roupas e ajudar comunidades em necessidade.

## Funcionalidades

- **Busca de Pontos de Coleta**: Usuários podem encontrar pontos de coleta próximos através de busca por CEP
- **Visualização em Mapa**: Integração com Google Maps para visualizar pontos de coleta geograficamente
- **Cadastro de Novos Pontos**: Formulário para entidades assistenciais solicitarem cadastro como ponto de coleta
- **Área Administrativa**: Sistema de gerenciamento de pontos de coleta protegido por autenticação
- **Design Responsivo**: Interface adaptável para dispositivos móveis e desktop
- **Recursos de Acessibilidade**: Opções para aumentar fonte e alto contraste

## Tecnologias Utilizadas

### Frontend
- HTML5
- CSS3
- JavaScript
- Google Maps API

### Backend
- Python
- Flask
- MySQL
- API ViaCEP e Nominatim para geolocalização

## Estrutura do Projeto

```
tem_agasalho_aqui/
├── static/               # Arquivos estáticos
│   ├── css/              # Folhas de estilo
│   ├── js/               # Scripts JavaScript
│   └── images/           # Imagens e ícones
├── templates/            # Templates HTML
├── database/             # Scripts de banco de dados
│   └── init_db.py        # Script de inicialização do banco
├── app.py                # Aplicação principal Flask
├── test_website.py       # Testes automatizados
├── prepare_deployment.py # Script para preparação de implantação
└── README.md             # Este arquivo
```

## Instalação e Configuração

### Requisitos
- Python 3.8 ou superior
- MySQL 5.7 ou superior
- Pip (gerenciador de pacotes Python)

### Passos para Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/RogerioVieira77/PI-III/tree/main/aplicacao/tem_agasalho_aqui.git
   cd tem_agasalho_aqui
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   ```
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

4. Inicialize o banco de dados:
   ```
   python database/init_db.py
   ```

5. Execute a aplicação:
   ```
   python app.py
   ```

6. Acesse a aplicação em seu navegador:
   ```
   http://localhost:5000
   ```

## Uso da Aplicação

### Para Doadores
1. Acesse a página inicial
2. Clique em "Quero Ajudar" ou navegue para "Pontos de Coleta"
3. Digite seu CEP na barra de pesquisa
4. Visualize os pontos de coleta próximos no mapa
5. Clique em um ponto para ver detalhes e informações de contato

### Para Entidades Assistenciais
1. Acesse a página "Cadastro"
2. Preencha o formulário com as informações da entidade
3. Envie a solicitação
4. A equipe administrativa analisará a solicitação e entrará em contato

### Para Administradores
1. Acesse a página "Administração"
2. Faça login com suas credenciais
3. Gerencie os pontos de coleta existentes
4. Adicione novos pontos de coleta

## Implantação em Produção

Para implantar a aplicação em um ambiente de produção, utilize o script de preparação para implantação:

```
python prepare_deployment.py
```

Este script criará um pacote de implantação com todos os arquivos necessários e instruções detalhadas.

## Credenciais Padrão

**Atenção**: Altere estas credenciais após a primeira instalação!

- **Email**: contatoagasalhoaqui@gmail.com
- **Senha**: admin123

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Contato

Para suporte ou dúvidas:
- Email: contatoagasalhoaqui@gmail.com
- Telefone: (11) 4002-0922

---

Desenvolvido por estudantes da UNIVESP © 2025