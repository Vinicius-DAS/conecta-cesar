# Deploy no Render

Passo a passo pra colocar o Conecta Cesar no ar, gratuito, pronto pra linkar do portfólio.

## Por que Render + Neon (não Vercel, não o Postgres do próprio Render)

- **Vercel** não serve — é feito pra frontend/funções serverless de vida curta. Esse projeto é Django com banco persistente e upload de arquivo, o que a Vercel não suporta.
- **O Postgres gratuito do próprio Render expira em 30 dias.** Como a ideia é deixar isso linkado no portfólio por muito tempo, uso o [Neon](https://neon.tech) pro banco — plano gratuito sem expiração (só "hiberna" quando fica muito tempo sem uso, e acorda sozinho na primeira query).

## 1. Criar o projeto no Neon (banco + storage)

1. Crie uma conta em [neon.tech](https://neon.tech) (dá pra usar login do GitHub).
2. Crie um projeto novo. **Região: escolha a mesma região do Render** (passo 2) — não tem região no Brasil em nenhum dos dois serviços, então o que importa é o banco/storage ficarem perto do servidor da aplicação, não do visitante. Ex.: "US East 2 (Ohio)" nos dois.
3. Deixe **Postgres database** ligado.
4. Ligue também **Object storage** e cria um bucket chamado `uploads`, visibilidade **Private**. Resolve o problema de uploads (fotos, atividades) sumirem a cada redeploy, já que o disco do Render no plano free não é persistente.
5. Depois de criado o projeto:
   - Em **Connect**, pegue a connection string do Postgres e separe em 4 valores (não use a string inteira): **Database name**, **Host**, **Role/User**, **Password**.
   - No bucket `uploads`, gere uma credencial (aparece **uma única vez**): `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL_S3`, `AWS_REGION`.

Guarde esses 8 valores — vai usar no próximo passo. Nenhum deles precisa ir num arquivo `.env` local; são colados direto no painel do Render.

## 2. Criar o serviço no Render

1. Crie uma conta em [render.com](https://render.com) (dá pra usar login do GitHub).
2. **New → Blueprint**, selecione o repositório `Vinicius-DAS/conecta-cesar` (branch `main`, depois que os PRs estiverem mergeados). Escolha a mesma região do projeto Neon (passo 1).
3. O Render detecta o `render.yaml` na raiz do repo automaticamente e mostra o serviço `conecta-cesar` pronto pra criar.
4. Quando pedir os 8 valores marcados como obrigatórios (`DBNAME`, `DBHOST`, `DBUSER`, `DBPASS`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL_S3`, `AWS_REGION`), cola os valores que você pegou do Neon no passo anterior. Os 4 do `AWS_*` são opcionais — se deixar em branco, os uploads voltam a usar o disco local (não persistente) em vez do bucket.
5. Confirma a criação — o Render builda e sobe o serviço automaticamente (leva alguns minutos no primeiro deploy).

O `render.yaml` já cuida do resto: `SECRET_KEY` gerado automaticamente, `DEBUG=0`, migrações aplicadas a cada deploy, arquivos estáticos coletados no build.

## 3. Popular com dados de demonstração

Depois do primeiro deploy funcionar, no painel do Render abra a aba **Shell** do serviço e rode:

```bash
python manage.py seed_demo_data
```

Isso cria os professores, turmas, disciplinas, alunos e todo o resto — veja `app_cc/management/commands/seed_demo_data.py` pra lista completa e as credenciais de login geradas (todas com senha `demo123`).

**Sobre uploads**: se você configurou o Object Storage da Neon no passo 1 (bucket `uploads` + as 4 variáveis `AWS_*` no Render), os arquivos enviados (fotos de perfil, atividades, etc.) sobrevivem a redeploys normalmente. Se pulou essa parte, o disco do plano gratuito do Render não é persistente — os uploads somem no próximo deploy (aceitável pra uma demo, mas evite depender disso).

## 4. Depois de estar no ar

Volta aqui e me manda a URL que o Render gerou (tipo `conecta-cesar.onrender.com`) que eu:
- Atualizo o link do projeto no seu portfólio.
- Corrijo a descrição do projeto lá (hoje diz "HTML, CSS, UX/UI", mas isso é um projeto Django/PostgreSQL completo).

## Nota sobre o "spin down"

No plano gratuito, o serviço "dorme" depois de um tempo sem acesso e demora uns 30-60 segundos pra acordar na primeira visita depois disso. É normal — só avisa quem for testar que a primeira carga pode ser mais lenta.
