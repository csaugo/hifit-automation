---
name: tag-de-preco
description: >
  This skill should be used when the user asks to "colocar preço na foto",
  "aplicar tag de preço", "tratar as fotos", "preparar imagens pro Instagram",
  "colocar etiqueta na imagem", or shares product photos that need the H! Fit
  neon price pill and brand chip before posting to Instagram.
metadata:
  version: "0.1.0"
---

# Tag de Preço — H! Fit

Aplicar a identidade H! Fit em fotos de produto: **pill neon de preço** (estilo aprovado da marca), **chip da marca do produto** e enquadramento correto para Instagram. Todo o processamento é feito pelo script `scripts/tag_preco.py`.

## Entradas necessárias

1. **Foto(s)** — arquivo(s) enviados pelo usuário (ou caminho na pasta hifit)
2. **Preço** — ex.: "R$ 189,90" (opcional: complemento "pronta entrega!", "últimas unidades!", "6x sem juros")
3. **Marca do produto** — para o chip (ALO YOGA, GYMSHARK, VIA MÁFIA, LIVE!…). Usar "H! FIT" se for peça própria

Se preço ou marca não forem informados, perguntar antes de processar.

## Processo

1. Copiar as fotos para um diretório de trabalho (uploads são read-only)
2. Executar o script para cada foto:

```bash
pip install pillow --break-system-packages -q 2>/dev/null
python3 "${CLAUDE_PLUGIN_ROOT}/skills/tag-de-preco/scripts/tag_preco.py" \
  --input foto.jpg --output foto-final.jpg \
  --preco "R$ 189,90" --extra "pronta entrega!" \
  --marca "VIA MÁFIA" --formato 4x5
```

3. **Sempre visualizar o resultado** (ler o arquivo de saída como imagem) e conferir: pill legível, chip não cobre o produto, corte não decapitou a modelo
4. Mostrar o resultado ao usuário para aprovação antes de publicar
5. Salvar as versões finais na pasta do post: `Documents/hifit/posts/AAAA-MM-DD-<slug>/`

## Parâmetros do script

| Flag | Valores | Default |
|---|---|---|
| `--formato` | `4x5` (feed 1080×1350), `1x1` (1080×1080), `9x16` (story 1080×1920) | `4x5` |
| `--preco` | texto da pill (obrigatório) | — |
| `--extra` | complemento após "·" na pill | vazio |
| `--marca` | texto do chip | vazio (sem chip) |
| `--pos-pill` | `baixo-esq`, `baixo-dir` | `baixo-esq` |
| `--sem-logo` | omite o selo "H!" no canto superior direito | logo ativo |

## Regras visuais (identidade aprovada)

- Pill neon: fundo #C6FF00, texto preto #0D0D0D em negrito condensado, cantos 100% arredondados, rotação −2°, sombra suave
- Chip de marca: fundo preto 82% opaco, texto branco em caixa alta com espaçamento, canto oposto ao da pill
- Selo "H!": quadrado arredondado neon com "H!" preto, canto superior direito, discreto (~6% da largura)
- Nunca cobrir o rosto da modelo nem o produto principal — se necessário, usar `--pos-pill baixo-dir`
- A cor neon é exclusiva da moldura H! Fit: não recolorir a foto do produto

## Vídeos (reels/stories)

Para aplicar a pill de preço em VÍDEO, gerar a pill como PNG transparente (rodar o script numa imagem em branco 1080x1920 e recortar, ou gerar via PIL direto) e sobrepor com ffmpeg:

```bash
ffmpeg -i video.mp4 -i pill.png -filter_complex \
  "[0:v][1:v]overlay=40:H-h-120" -c:a copy -y video-final.mp4
```

Manter a pill nos primeiros 3s ou o vídeo todo; nunca cobrir rosto. Formato alvo: 1080x1920 (9:16), H.264 + AAC.

## Checklist antes de aprovar

- [ ] Texto da pill correto (preço confere com o informado)
- [ ] Marca escrita corretamente no chip
- [ ] Formato certo para o destino (4x5 feed · 9x16 story)
- [ ] Nada importante cortado ou coberto
