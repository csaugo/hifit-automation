---
name: tag-de-preco
description: >
  This skill should be used when the user asks to "tratar as fotos",
  "preparar imagens pro Instagram", "colocar o selo H!", or shares product
  photos for a feed post. By default it crops/resizes to the target format
  and stamps only the small neon "H!" seal (top-right) — no price pill, no
  brand chip, since feed posts are a showcase and pricing lives in the bio
  catalog. The price-pill and brand-chip overlay is legacy/opt-in, only for
  an explicit one-off request (e.g. a flash-sale post).
metadata:
  version: "0.2.0"
---

# Tag de Preço — H! Fit

Aplicar a identidade H! Fit em fotos de produto para o feed: **crop/resize para o formato certo** e o **selo neon "H!"** no canto superior direito — a marca do post. Por padrão **não** se aplica pill de preço nem chip de marca: feed é mostruário, preço fica só na legenda (via `skills/criar-post/SKILL.md`), e o catálogo com preços vive no link da bio. A pill de preço e o chip de marca continuam disponíveis no script, mas são **opcionais**, usados só quando o Cadu pedir explicitamente algo pontual (ex.: post de promoção/liquidação). Todo o processamento é feito pelo script `scripts/tag_preco.py`.

## Entradas necessárias

1. **Foto(s)** — arquivo(s) enviados pelo usuário (ou caminho na pasta hifit)
2. **Formato desejado** — `4x5` (padrão, feed), `1x1` ou `9x16` (story), se o usuário pedir outro

Preço e marca do produto **não são necessários** para tratar a imagem — eles só importam para a legenda (`skills/criar-post/SKILL.md`). Só pergunte por preço/marca aqui se o Cadu pedir explicitamente a pill/chip pontual (ver seção "Pill de preço e chip de marca (opcional)" abaixo).

## Processo

1. Copiar as fotos para um diretório de trabalho (uploads são read-only)
2. Executar o script para cada foto (comportamento padrão — sem pill, sem chip):

```bash
pip install pillow --break-system-packages -q 2>/dev/null
python3 "${CLAUDE_PLUGIN_ROOT}/skills/tag-de-preco/scripts/tag_preco.py" \
  --input foto.jpg --output foto-final.jpg \
  --formato 4x5
```

3. **Sempre visualizar o resultado** (ler o arquivo de saída como imagem) e conferir: corte não decapitou a modelo, selo H! visível e discreto no canto superior direito, nada mais foi desenhado por cima da foto
4. Mostrar o resultado ao usuário para aprovação antes de publicar
5. Salvar as versões finais na pasta do post: `Documents/hifit/posts/AAAA-MM-DD-<slug>/`

## Parâmetros do script

| Flag | Valores | Default |
|---|---|---|
| `--formato` | `4x5` (feed 1080×1350), `1x1` (1080×1080), `9x16` (story 1080×1920) | `4x5` |
| `--preco` | **opcional** — texto da pill (só usar se o Cadu pedir uma pill de preço pontual; omitido por padrão) | vazio (sem pill) |
| `--extra` | complemento após "·" na pill, só relevante se `--preco` for usado | vazio |
| `--marca` | **opcional** — texto do chip de marca (só usar se o Cadu pedir o chip pontual; omitido por padrão) | vazio (sem chip) |
| `--pos-pill` | `baixo-esq`, `baixo-dir` — só relevante se `--preco` for usado | `baixo-esq` |
| `--sem-logo` | omite o selo "H!" no canto superior direito (raramente usado — o selo é a identidade padrão do post) | logo ativo |

## Carrossel (padrão): mesmo tratamento em todas as fotos

Diferente do fluxo antigo, **não há mais distinção entre a primeira foto e as demais**: todas as fotos de um carrossel levam exatamente o mesmo tratamento — crop/resize pro formato + selo H!, sem pill nem chip. Rode o mesmo comando pra cada `foto-N.jpg`:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/tag-de-preco/scripts/tag_preco.py" \
  --input foto-1.jpg --output foto-1-final.jpg --formato 4x5

python3 "${CLAUDE_PLUGIN_ROOT}/skills/tag-de-preco/scripts/tag_preco.py" \
  --input foto-2.jpg --output foto-2-final.jpg --formato 4x5
```

## Pill de preço e chip de marca (opcional — só sob pedido explícito)

Só use `--preco`/`--extra`/`--marca` quando o Cadu pedir explicitamente uma badge de preço na imagem (ex.: "bota o preço na foto dessa vez", post de liquidação pontual). Nesse caso, siga a convenção antiga: pill de preço só na primeira foto (a capa), demais fotos sem `--preco`:

```bash
# foto 1 (capa): pill de preço + chip + selo — só se pedido explicitamente
python3 "${CLAUDE_PLUGIN_ROOT}/skills/tag-de-preco/scripts/tag_preco.py" \
  --input foto-1.jpg --output foto-1-final.jpg \
  --preco "R$ 189,90" --marca "VIA MÁFIA" --formato 4x5

# fotos 2+: sem pill, só chip + selo
python3 "${CLAUDE_PLUGIN_ROOT}/skills/tag-de-preco/scripts/tag_preco.py" \
  --input foto-2.jpg --output foto-2-final.jpg \
  --marca "VIA MÁFIA" --formato 4x5
```

Se preço ou marca faltarem nesse fluxo opcional, pergunte antes de processar.

## Regras visuais (identidade aprovada)

- Selo "H!": quadrado arredondado neon com "H!" preto, canto superior direito, discreto (~6% da largura) — **sempre presente por padrão**, é a única marca visual no feed
- Nunca cobrir o rosto da modelo nem o produto principal no crop
- A cor neon é exclusiva da moldura H! Fit: não recolorir a foto do produto
- **Só quando pill/chip forem usados sob pedido explícito** (ver seção acima): pill neon fundo #C6FF00, texto preto #0D0D0D em negrito condensado, cantos 100% arredondados, rotação −2°, sombra suave; chip de marca fundo preto 82% opaco, texto branco em caixa alta, canto oposto ao da pill; usar `--pos-pill baixo-dir` se a pill cobrir algo importante

## Vídeos (reels/stories)

Isto é sempre um caso pontual (a pill não é usada por padrão em fotos, e muito menos em vídeo) — só siga esta seção se o Cadu pedir explicitamente. Para aplicar a pill de preço em VÍDEO, gerar a pill como PNG transparente (rodar o script numa imagem em branco 1080x1920 e recortar, ou gerar via PIL direto) e sobrepor com ffmpeg:

```bash
ffmpeg -i video.mp4 -i pill.png -filter_complex \
  "[0:v][1:v]overlay=40:H-h-120" -c:a copy -y video-final.mp4
```

Manter a pill nos primeiros 3s ou o vídeo todo; nunca cobrir rosto. Formato alvo: 1080x1920 (9:16), H.264 + AAC.

## Checklist antes de aprovar

- [ ] Formato certo para o destino (4x5 feed · 9x16 story)
- [ ] Selo H! visível no canto superior direito, discreto, sem cobrir nada importante
- [ ] Nada importante cortado ou coberto no crop
- [ ] Nenhuma pill/chip apareceu, a menos que tenha sido pedido explicitamente pelo Cadu
- [ ] Se pill/chip foram usados por pedido explícito: texto do preço confere, marca escrita corretamente, pill só na foto de capa
