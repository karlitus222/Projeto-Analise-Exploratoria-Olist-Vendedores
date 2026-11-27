# Compartilhar a versão revisada sem alterar o GitHub

O endereço `http://127.0.0.1:8503/` abre a revisão de 27/11/2026 somente neste computador.
Para colegas em outros computadores ou celulares, é necessário um endereço público.

## Link temporário

O utilitário oficial Cloudflare Tunnel 2026.11.2 foi baixado neste computador em `.tools/cloudflared.exe`.
O SHA256 do download foi conferido contra o publicado pela Cloudflare:
`555b46c85582461d189cac30d14ad05480d612613801be9f110b8ce08c5b2113`.

A tentativa automática de iniciar o túnel foi bloqueada pela revisão de aprovação. Nenhum túnel foi iniciado por essa tentativa.
O proprietário pode iniciar o compartilhamento manualmente, no terminal desta pasta:

```powershell
.\.tools\cloudflared.exe tunnel --no-autoupdate --url http://127.0.0.1:8503 --protocol http2
```

Usar o endereço HTTPS terminado em `trycloudflare.com` exibido no terminal.
Qualquer pessoa com esse endereço poderá abrir o painel. O computador, o painel e o terminal do túnel precisam permanecer ligados.
Pressionar `Ctrl+C` no terminal do túnel encerra o compartilhamento. Um novo túnel normalmente gera outro endereço.

O ZIP da etapa 7 não inclui executáveis, logs nem `.tools/`. Para compartilhar a partir de outra máquina,
obter o utilitário em https://developers.cloudflare.com/tunnel/downloads/ e iniciar antes o painel:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8503 --server.address 127.0.0.1
```

Referência do compartilhamento temporário: https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/

Nenhum código foi enviado ao GitHub, e nenhuma hospedagem Render foi criada.
O link público anterior do Streamlit continua mostrando a versão publicada do repositório, sem os ajustes exclusivos desta cópia local.
