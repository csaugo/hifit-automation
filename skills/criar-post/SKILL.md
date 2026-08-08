---
name: criar-post
description: >
  This skill should be used when the user asks to "criar um post", "escrever legenda",
  "fazer post do produto", "criar chamada", "criar hashtags", "post pro Instagram da H! Fit",
  or shares product photos wanting Instagram content for the @hifit.br store account.
  Generates caption, hook, CTA, hashtags and first comment in the H! Fit brand voice.
metadata:
  version: "0.1.0"
---

# Criar Post — H! Fit (@hifit.br)

Gerar o pacote de texto completo de um post de Instagram da loja H! Fit, sempre na voz da marca. Ler `references/voz-e-copy.md` antes de escrever qualquer legenda. Para decisões finas de tom (público, contexto de atendimento, léxico banido, exemplos calibrados), consultar o documento oficial completo em `references/tom-e-voz-completo.md` (Tom e Voz v1.1).

## Informações necessárias

Coletar do usuário (perguntar apenas o que faltar; usar AskUserQuestion quando disponível):

1. **Produto**: nome da peça, marca (Alo Yoga, Gymshark, Via Máfia, LIVE!, etc.), cores/tamanhos disponíveis
2. **Preço** e condição (à vista, parcelado, promoção)
3. **Gancho comercial**: novidade, últimas unidades, drop, reposição, promoção
4. **Formato**: post único, carrossel ou reel (default: post único se 1 foto, carrossel se 2+)

## Estrutura obrigatória da legenda

```
[GANCHO — 1 linha, urgência ou novidade, com emoji ⚡🔥💚]

[PRODUTO — marca + nome + diferencial em 1-2 linhas]
[Tamanhos disponíveis + preço com "·" separando condições]

[CTA — 1 linha]

Vista sua Força 💚⚡

.
[hashtags no primeiro comentário — nunca na legenda]
```

## Regras da marca (inegociáveis)

- Slogan: **"Vista sua Força"** — sem exclamação no texto (o "!" pertence à logomarca H!FIT)
- Frases curtas, imperativas, energia de treino: "corre", "garante a sua", "chegou hoje"
- Nunca usar caixa alta em frases inteiras na legenda (caixa alta é só para tiles visuais)
- Sempre citar a marca do produto — o posicionamento é multimarcas: "as marcas que aguentam seu treino"
- Emojis permitidos: ⚡💚🔥💪🖤 (máx. 3 por legenda)
- Preço sempre no formato "R$ 189,90" e, quando parcelado, "3x de R$ 63,30 sem juros"
- CTAs padrão (variar): "Link na bio", "Chama no direct pra reservar", "Corre pra loja", "Toca na sacola"

## Hashtags (primeiro comentário)

Montar 10–15 no formato: 2 da marca H! Fit + 3 da marca do produto + 4 de categoria + 3 locais/comunidade. Consultar a tabela pronta em `references/voz-e-copy.md`. #VistaSuaForça e #HFit são obrigatórias.

## Saída

Entregar sempre neste formato:

```
📝 LEGENDA
<texto final>

💬 PRIMEIRO COMENTÁRIO
<hashtags>

🎯 SUGESTÃO DE HORÁRIO
<ver tabela de horários em references/voz-e-copy.md>

🖼 ALT TEXT (acessibilidade)
<descrição da foto em 1 frase>
```

Depois de aprovado o texto, se houver fotos a tratar, acionar a skill `tag-de-preco`; para publicar, acionar a skill `publicar-instagram`.
