---
name: criar-story
description: >
  This skill should be used when the user asks for a "story", "stories",
  "criativo pra story", a promo video or promo image for Instagram Stories,
  or asks to generate an image/video asset from scratch (with or without
  source photos). Builds 1080x1920 creatives — static JPEG or MP4 video —
  with the H! Fit identity burned in, ready for publishing via the official
  Graph API (which supports no stickers, links or captions on stories).
metadata:
  version: "0.1.0"
---

# Criar Story — H! Fit

Gerar criativos de Instagram Stories (e assets avulsos) a partir de foto(s) enviadas OU do zero (texto descrevendo o que se quer). O resultado é sempre um arquivo final com todo o texto/CTA/identidade **queimado no pixel** — a API de publicação de Stories não aceita sticker, link clicável, caption nem música.

## Matriz de decisão do caminho

| Pedido | Fotos enviadas | Caminho |
|---|---|---|
| Imagem de story / tratamento simples (crop, texto, badge) | 1+ (usa a 1ª) | **Local**: `scripts/story_creative.py --mode image` |
| Tratamento generativo ("troca o fundo", "põe em cenário X") | 1+ | **Higgsfield** `generate_image` (edição) → depois camada de texto local |
| Vídeo de story | 1 foto | **Local**: ffmpeg Ken Burns (padrão) — Higgsfield só se o pedido exigir movimento generativo (modelo andando, cena animada) |
| Vídeo de story | 2+ fotos | **Higgsfield** image-to-video com as fotos → re-encode ffmpeg → camada de texto local |
| Imagem (story ou post) | nenhuma | **Higgsfield** text-to-image (produto/cena descritos no pedido) → camada de identidade local. Se for arte puramente tipográfica/gráfica (só texto e cores), gerar direto no local com o script |
| Vídeo (story ou post) | nenhuma | **Higgsfield** text-to-video → re-encode → camada de texto local |

Regras gerais:
- **Imagem vs vídeo**: só gere vídeo se o pedido mencionar vídeo/animação/movimento. Na dúvida, imagem (mais rápido e barato).
- **Duração de vídeo**: a informada no pedido ("6s", "10 segundos"); default **7s** se pediu vídeo sem duração. Clamp em **3–60s** (limite da API) — se clampar, avise o usuário na mensagem final.
- **Higgsfield**: máximo **1 geração por pedido** (consome créditos do Cadu) — sem variações extras não solicitadas. Use `models_explore(action:'recommend')` na dúvida sobre o modelo; importe fotos com `media_import_url` (as URLs públicas do Supabase); aguarde com `jobs_wait`; baixe o resultado.
- Se o conector Higgsfield não estiver disponível na execução: multi-foto → fallback slideshow local (ffmpeg, cortes com crossfade `xfade` entre as fotos, mesmo encoding abaixo); pedido de geração do zero → avise o usuário que a geração por IA está indisponível nesta execução e não invente um asset.

## Canvas e safe zones (story 1080x1920)

A UI do Instagram cobre o topo (barra de progresso, avatar) e o rodapé (caixa de resposta):

```
y=0    ┌──────────────┐
       │  UI DO IG    │  ← nada importante até y=250
y=250  ├──────────────┤
       │              │
       │  ÁREA ÚTIL   │  ← todo texto/badge/CTA aqui
       │              │     (CTA ideal: y≈1200–1600)
y=1670 ├──────────────┤
       │  UI DO IG    │  ← nada importante abaixo
y=1920 └──────────────┘     margens laterais: 60px
```

O `story_creative.py` já posiciona tudo dentro dessas zonas por construção — não desenhe texto fora dele.

## Copy e conversão (stories ≠ feed)

- **Oferta/desconto visível desde o frame 0** — em vídeo, a camada de texto entra desde o primeiro frame (nada de revelar a oferta só no final; quase metade dos viewers abandona em 3s).
- **Uma mensagem por story.** Headline curta e punchy; se não dá pra ler num relance, tem texto demais.
- **Preço/desconto explícito e GRANDE.** Atenção: isso é o OPOSTO da regra do feed (feed = mostruário, sem preço na imagem). Story é canal de promoção — aqui a badge neon de desconto/preço é bem-vinda e central.
- Texto sempre com caixa de apoio translúcida (o script faz) — legibilidade sobre qualquer foto.
- Voz da marca: seguir `skills/criar-post/references/` (tom, "Vista sua Força 💚", formato de preço "R$ 179,90").
- **Nunca prometa link clicável** ("arrasta pra cima", "toca no link") — a API não publica sticker de link. Se o pedido incluir um link, escreva-o legível na arte (ex.: "hifit.store") ou use CTA "link na bio". Sticker clicável só manualmente pelo app, depois de publicado.
- **Nunca invente desconto/preço não informado.** Pedido sem promoção → story vitrine (produto + marca + CTA).

## Pipeline — imagem (local)

```bash
pip install pillow --break-system-packages -q 2>/dev/null
python3 skills/criar-story/scripts/story_creative.py --mode image \
  --input foto.jpg --output story.jpg \
  --headline "Super promoção" --destaque "30% OFF" \
  --produto "Conjunto Solar Flex · Via Máfia" --preco "R$ 179,90" \
  --cta "Garanta o seu — link na bio"
```

Saída: JPEG 1080x1920 (a API só aceita JPEG — nunca envie PNG), ≤8MB (o script reduz a qualidade sozinho se precisar). Use só as flags que o pedido justificar (todas opcionais). **Sempre visualize o resultado** (leia o arquivo como imagem) antes de enviar.

## Pipeline — vídeo local (1 foto, Ken Burns)

1. Gere a camada de texto: `story_creative.py --mode overlay --output overlay.png` (mesmas flags de texto).
2. Monte o vídeo (exemplo pra 7s; ajuste `-t` e `d=<segundos*30>`):

```bash
which ffmpeg || (apt-get update -qq && apt-get install -y -qq ffmpeg) || pip install imageio-ffmpeg --break-system-packages -q
ffmpeg -y -loop 1 -i foto.jpg \
  -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 \
  -i overlay.png \
  -filter_complex "[0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,\
scale=4000:-1,zoompan=z='if(eq(on,1),1,min(zoom+0.0008,1.12))':\
x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=210:s=1080x1920:fps=30,\
fade=t=in:st=0:d=0.4,fade=t=out:st=6.6:d=0.4[bg];\
[bg][2]overlay=0:0,format=yuv420p[v]" \
  -map "[v]" -map 1:a -t 7 \
  -c:v libx264 -profile:v high -pix_fmt yuv420p \
  -r 30 -g 60 -keyint_min 60 -sc_threshold 0 \
  -b:v 6M -maxrate 8M -bufsize 12M \
  -c:a aac -b:a 128k -ar 48000 -ac 2 -shortest \
  -movflags +faststart story.mp4
```

Pontos não-negociáveis do encoding (requisitos da Meta): `yuv420p`, closed GOP (`-g 60 -keyint_min 60 -sc_threshold 0`), `-movflags +faststart`, AAC 48kHz, re-encode limpo (nunca `-c copy`/concat — gera edit lists que a Meta rejeita). O fade é só no fundo `[bg]` — o overlay de texto entra por cima SEM fade, visível desde o frame 0. Se o zoompan ficar lento demais, troque `scale=4000:-1` por `scale=2160:-1`.

## Pipeline — Higgsfield (multi-foto, generativo, ou do zero)

1. **Com fotos**: importe cada URL pública do Supabase com `media_import_url`. **Sem fotos**: escreva um prompt de geração descrevendo produto/cena a partir do pedido (estética fitness da marca; sem texto na imagem — o texto entra depois pela camada local).
2. Gere com `generate_video` (ou `generate_image`) — 1 geração só. Aspect 9:16 quando o modelo permitir. Aguarde com `jobs_wait`.
3. Baixe o resultado (`curl -sSL -o bruto.mp4 "<url do resultado>"`).
4. **Sempre re-encode** o vídeo pro spec de story (o resultado da geração não garante H.264/yuv420p/faststart/duração):

```bash
ffmpeg -y -i bruto.mp4 -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -i overlay.png \
  -filter_complex "[0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg];\
[bg][2]overlay=0:0,format=yuv420p[v]" \
  -map "[v]" -map 1:a -t <duração ≤60> \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -r 30 -g 60 -keyint_min 60 -sc_threshold 0 \
  -b:v 6M -maxrate 8M -bufsize 12M -c:a aac -b:a 128k -ar 48000 -ac 2 -shortest \
  -movflags +faststart story.mp4
```
   (se o vídeo gerado já tiver áudio que valha manter, troque o `-map 1:a` pelo áudio dele re-encodado pra AAC 48kHz)
5. Imagem gerada → passar pelo `story_creative.py --mode image --input gerada.jpg ...` pra ganhar a camada de identidade.

## Checklist de validação (antes de subir/enviar)

- [ ] Imagem: JPEG (não PNG), 1080x1920, ≤8MB
- [ ] Vídeo: `ffprobe story.mp4` → h264, yuv420p, 1080x1920, duração 3–60s, stream de áudio AAC presente, ≤100MB
- [ ] Vídeo >18MB → re-encodar com `-b:v 4M -maxrate 5M` (limite de 20MB do sendVideo por URL no Telegram)
- [ ] Texto legível, dentro das safe zones, oferta visível no frame 0 (vídeo)
- [ ] Nenhum desconto/preço que não foi informado no pedido
- [ ] Visualizou o resultado (imagem, ou 1 frame do vídeo via `ffmpeg -ss 0 -frames:v 1`)
