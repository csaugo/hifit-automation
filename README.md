# hifit-automation

Repositório dedicado à automação "Telegram → Claude Code Routine → Instagram/Facebook" da loja H! Fit (@hifit.br).

Este repo **não roda sozinho** — ele é o material que uma [Claude Code Routine](https://code.claude.com/docs/en/routines) clona a cada execução. Quem dispara a Routine é o serviço de webhook do Telegram, que vive separadamente na VPS (ver pasta `telegram-relay-service/` no pacote entregue, fora deste repo).

## Estrutura

- `ROUTINE_PROMPT.md` — texto exato para colar no campo "Instructions" da Routine.
- `skills/criar-post/` — skill que escreve legenda, hashtags, CTA e alt text na voz H! Fit.
- `skills/tag-de-preco/` — skill + script Python que aplica a pill neon de preço e o chip de marca na foto.
- `brand/` — guias de marca (tom e voz, guia de imagens) usados como referência de apoio.

## Segurança

Nenhum segredo (token do bot, chaves do Supabase, tokens do Meta) deve ser commitado neste repositório. Tudo isso fica como variável de ambiente configurada direto no "Environment" da Routine em claude.ai/code/routines — ver o runbook (`RUNBOOK.md`) entregue junto para o passo a passo completo.

## Escopo atual (Fase 1)

A Routine prepara o material (imagem tratada + legenda + hashtags + alt text) e devolve tudo pelo Telegram. O passo de salvar como rascunho no Meta Business Suite ainda é manual — ver `ROUTINE_PROMPT.md` para o racional.
