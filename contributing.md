# Contribuindo para o Projeto Conecta Cesar 🤝

Bem-vindo ao projeto Conecta Cesar! Obrigado por considerar contribuir. Este guia cobre a configuração do ambiente de desenvolvimento e o processo de contribuição.

## Pré-requisitos

- [Python](https://www.python.org/downloads/) 3.12+
- [Node.js](https://nodejs.org/) (só necessário se for rodar os testes E2E do Cypress)
- [Git](https://git-scm.com/downloads)

## Configurando o ambiente

### 1. Clone o repositório

```bash
git clone https://github.com/Vinicius-DAS/conecta-cesar.git
cd conecta-cesar/conecta-cesar
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv
```

No Windows:
```bash
.\venv\Scripts\activate
```

No macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o `.env`

```bash
cp .env.example .env
```

O padrão (`TARGET_ENV=Dev`) já é suficiente para rodar localmente com SQLite — as demais variáveis só importam em produção. Veja `.env.example` para a lista completa.

### 5. Rode as migrações

```bash
python manage.py migrate
```

### 6. (Opcional) Popule com dados de exemplo

```bash
python manage.py seed_demo_data
```

Cria professores, turmas, disciplinas, alunos e conteúdo em todas as áreas do sistema — login com qualquer usuário criado, senha `demo123`. Veja `app_cc/management/commands/seed_demo_data.py` para a lista completa.

### 7. Rode o servidor

```bash
python manage.py runserver
```

Acesse em [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Rodando os testes

```bash
# Testes unitários (Django)
python manage.py test

# Testes E2E (Cypress) — precisa do servidor rodando em outro terminal
npm ci
npx cypress open   # interface interativa
npx cypress run    # linha de comando
```

## Contribuindo com código

1. **Escolha uma issue** — dê uma olhada nas [issues abertas](https://github.com/Vinicius-DAS/conecta-cesar/issues).
2. **Fork** o repositório para sua conta.
3. **Crie uma branch** para sua contribuição:
   ```bash
   git checkout -b nova-feature
   ```
4. Desenvolva suas alterações, seguindo as diretrizes abaixo.
5. **Teste localmente** antes de abrir o PR (unitários + E2E se relevante).
6. **Commit e push**:
   ```bash
   git commit -m "Adicionar nova feature"
   git push origin nova-feature
   ```
7. **Abra um Pull Request** explicando as alterações.

### Diretrizes de desenvolvimento 🤔

- Siga boas práticas de codificação em Python, HTML e CSS.
- Formatação e ordem de imports consistentes com o resto do código.
- PRs que não seguirem essas diretrizes serão devolvidos para ajustes antes da aprovação.

## Dúvidas?

Abra uma issue, ou entre em contato com vdas@cesar.school.
