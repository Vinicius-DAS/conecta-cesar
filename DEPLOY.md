# Deploy no Render

Passo a passo pra colocar o Conecta Cesar no ar, gratuito, pronto pra linkar do portfólio.

## Por que Render + Neon (não Vercel, não o Postgres do próprio Render)

- **Vercel** não serve — é feito pra frontend/funções serverless de vida curta. Esse projeto é Django com banco persistente e upload de arquivo, o que a Vercel não suporta.
- **O Postgres gratuito do próprio Render expira em 30 dias.** Como a ideia é deixar isso linkado no portfólio por muito tempo, uso o [Neon](https://neon.tech) pro banco — plano gratuito sem expiração (só "hiberna" quando fica muito tempo sem uso, e acorda sozinho na primeira query).

## 1. Criar o banco no Neon

1. Crie uma conta em [neon.tech](https://neon.tech) (dá pra usar login do GitHub).
2. Crie um projeto novo — qualquer nome, região mais próxima do Brasil se tiver.
3. No painel do projeto, vá em **Connection Details**. Você vai precisar de 4 valores separados (não da connection string inteira):
   - **Database name**
   - **Host**
   - **Role/User**
   - **Password**

Guarde esses 4 valores — vai usar no próximo passo.

## 2. Criar o serviço no Render

1. Crie uma conta em [render.com](https://render.com) (dá pra usar login do GitHub).
2. **New → Blueprint**, selecione o repositório `Vinicius-DAS/conecta-cesar` (branch `main`, depois que os PRs estiverem mergeados).
3. O Render detecta o `render.yaml` na raiz do repo automaticamente e mostra o serviço `conecta-cesar` pronto pra criar.
4. Quando pedir os 4 valores marcados como obrigatórios (`DBNAME`, `DBHOST`, `DBUSER`, `DBPASS`), cola os valores que você pegou do Neon no passo anterior.
5. Confirma a criação — o Render builda e sobe o serviço automaticamente (leva alguns minutos no primeiro deploy).

O `render.yaml` já cuida do resto: `SECRET_KEY` gerado automaticamente, `DEBUG=0`, migrações aplicadas a cada deploy, arquivos estáticos coletados no build.

## 3. Popular com dados de demonstração

Depois do primeiro deploy funcionar, no painel do Render abra a aba **Shell** do serviço e rode:

```bash
python manage.py seed_demo_data
```

Isso cria os professores, turmas, disciplinas, alunos e todo o resto — veja `app_cc/management/commands/seed_demo_data.py` pra lista completa e as credenciais de login geradas (todas com senha `demo123`).

**Atenção**: o disco do plano gratuito do Render não é persistente — qualquer arquivo enviado por upload (fotos de perfil, atividades, etc.) some no próximo deploy. Pra um projeto de demonstração de portfólio isso é aceitável; se um dia quiser uploads que sobrevivem a redeploys, precisaria de um disco pago no Render ou um storage externo tipo S3/Cloudflare R2 — fora do escopo de "pronto pra demonstração".

## 4. Depois de estar no ar

Volta aqui e me manda a URL que o Render gerou (tipo `conecta-cesar.onrender.com`) que eu:
- Atualizo o link do projeto no seu portfólio.
- Corrijo a descrição do projeto lá (hoje diz "HTML, CSS, UX/UI", mas isso é um projeto Django/PostgreSQL completo).

## Nota sobre o "spin down"

No plano gratuito, o serviço "dorme" depois de um tempo sem acesso e demora uns 30-60 segundos pra acordar na primeira visita depois disso. É normal — só avisa quem for testar que a primeira carga pode ser mais lenta.
