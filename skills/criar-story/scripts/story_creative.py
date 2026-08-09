#!/usr/bin/env python3
"""
Story Creative H! Fit — monta o criativo de story (1080x1920) ou a camada de
texto transparente pra sobrepor em vídeo.

Identidade: preto #0D0D0D · neon #C6FF00 · selo H! · caixas de apoio translúcidas.
Todo texto fica dentro das safe zones do Instagram Stories (y=250..1670).

Modos:
  --mode image    foto de fundo + camada de texto -> JPEG final (story pronto)
  --mode overlay  só a camada de texto -> PNG transparente (pra overlay no ffmpeg)

Uso:
  python3 story_creative.py --mode image --input foto.jpg --output story.jpg \
      --headline "SUPER PROMOÇÃO" --destaque "30% OFF" \
      --produto "Conjunto Solar Flex · Via Máfia" --preco "R$ 179,90" \
      --cta "Garanta o seu — link na bio"

  python3 story_creative.py --mode overlay --output overlay.png \
      --headline "SUPER PROMOÇÃO" --destaque "30% OFF" --cta "Corre lá 🏃"
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

NEON = (198, 255, 0, 255)        # #C6FF00
PRETO = (13, 13, 13, 255)        # #0D0D0D
BRANCO = (255, 255, 255, 255)
CAIXA = (13, 13, 13, 170)        # caixa de apoio translúcida atrás de texto

FORMATOS = {"story": (1080, 1920), "4x5": (1080, 1350)}

# Safe zones do story (canvas 1080x1920): UI do Instagram cobre topo e rodapé
SAFE_TOP = 250
SAFE_BOTTOM = 1670
MARGEM_LATERAL = 60


# ---------------------------------------------------------------------------
# Helpers portados de skills/tag-de-preco/scripts/tag_preco.py (mesma identidade)
# ---------------------------------------------------------------------------

def font_path():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "..", "tag-de-preco", "assets", "Poppins-Bold.ttf"),
        os.path.join(here, "..", "..", "tag-de-preco", "assets", "DejaVuSansCondensed-Bold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            path = os.path.abspath(c)
            # fonte precisa cobrir acentos pt-BR (ç ã õ) — senão cai pra próxima
            try:
                f = ImageFont.truetype(path, 40)
                if f.getmask("ç").getbbox() is not None:
                    return path
            except Exception:
                continue
    sys.exit("Nenhuma fonte com suporte a pt-BR encontrada — adicione um .ttf em tag-de-preco/assets/")


def cover_crop(img, size):
    """Corta a imagem para preencher o formato (crop central com viés para o topo)."""
    img = ImageOps.exif_transpose(img).convert("RGB")
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = int((nh - th) * 0.30)  # viés para o topo: preserva rosto/torso
    return img.crop((left, top, left + tw, top + th))


def rounded_pill(text, font, pad_x, pad_y, bg, fg):
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    box = d.textbbox((0, 0), text, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    img = Image.new("RGBA", (w + 2 * pad_x, h + 2 * pad_y), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = img.height // 2
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=r, fill=bg)
    d.text((pad_x - box[0], pad_y - box[1]), text, font=font, fill=fg)
    return img


def paste_with_shadow(base, layer, xy, angle=0.0):
    if angle:
        layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    alpha = layer.split()[3].point(lambda a: int(a * 0.45))
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 115))
    shadow.putalpha(alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    base.alpha_composite(shadow, (xy[0] + 4, xy[1] + 7))
    base.alpha_composite(layer, xy)


def selo_h(width):
    """Selo 'H!' neon (mesma identidade do tag_preco)."""
    s = round(width * 0.062)
    selo = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(selo)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=round(s * 0.24), fill=NEON)
    f = ImageFont.truetype(font_path(), round(s * 0.56))
    tb = d.textbbox((0, 0), "H!", font=f)
    d.text(((s - (tb[2] - tb[0])) / 2 - tb[0], (s - (tb[3] - tb[1])) / 2 - tb[1]),
           "H!", font=f, fill=PRETO)
    return selo


# ---------------------------------------------------------------------------
# Camada de texto do story
# ---------------------------------------------------------------------------

def _wrap(text, font, max_w, draw):
    """Word-wrap simples baseado na largura real do texto."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if draw.textlength(cand, font=font) <= max_w:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _fit_font(text, fp, size, max_w, draw, min_size=36):
    """Reduz a fonte até a MAIOR palavra caber na largura útil."""
    while size > min_size:
        font = ImageFont.truetype(fp, size)
        if all(draw.textlength(w, font=font) <= max_w for w in text.split()):
            return font
        size -= 4
    return ImageFont.truetype(fp, min_size)


def _draw_boxed_lines(layer, draw, lines, font, y, fill=BRANCO, box=CAIXA, align_center=True):
    """Desenha linhas com caixa de apoio translúcida; devolve o y após o bloco."""
    W = layer.width
    pad_x, pad_y, gap = 28, 14, 10
    for line in lines:
        tw = draw.textlength(line, font=font)
        bbox = draw.textbbox((0, 0), line, font=font)
        th = bbox[3] - bbox[1]
        bw, bh = tw + 2 * pad_x, th + 2 * pad_y
        x = (W - bw) // 2 if align_center else MARGEM_LATERAL
        draw.rounded_rectangle([x, y, x + bw, y + bh], radius=16, fill=box)
        draw.text((x + pad_x - bbox[0], y + pad_y - bbox[1]), line, font=font, fill=fill)
        y += bh + gap
    return y


def build_text_layer(size, headline="", destaque="", produto="", preco="", cta="", with_logo=True):
    W, H = size
    is_story = (W, H) == FORMATOS["story"]
    top = SAFE_TOP if is_story else round(H * 0.06)
    bottom = SAFE_BOTTOM if is_story else H - round(H * 0.06)
    max_w = W - 2 * MARGEM_LATERAL

    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    fp = font_path()

    # selo H! — canto superior direito, logo abaixo da safe zone
    if with_logo:
        s = selo_h(W)
        layer.alpha_composite(s, (W - s.width - MARGEM_LATERAL, top + 16))

    y = top + round(H * 0.06)

    # headline — mensagem principal, grande
    if headline:
        font = _fit_font(headline, fp, round(W * 0.078), max_w, draw)
        lines = _wrap(headline.upper(), font, max_w, draw)
        y = _draw_boxed_lines(layer, draw, lines, font, y)
        y += 18

    # destaque — badge neon rotacionada (ex.: "30% OFF")
    if destaque:
        font = ImageFont.truetype(fp, round(W * 0.095))
        pill = rounded_pill(destaque, font, round(W * 0.045), round(W * 0.025), NEON, PRETO)
        if pill.width > max_w:
            font = ImageFont.truetype(fp, round(W * 0.07))
            pill = rounded_pill(destaque, font, round(W * 0.04), round(W * 0.022), NEON, PRETO)
        paste_with_shadow(layer, pill, ((W - pill.width) // 2, y), angle=2.0)
        draw = ImageDraw.Draw(layer)  # o composite invalida o draw anterior
        y += pill.height + round(H * 0.03)

    # produto + preço — bloco do meio
    if produto:
        font = _fit_font(produto, fp, round(W * 0.045), max_w, draw)
        lines = _wrap(produto, font, max_w, draw)
        y = _draw_boxed_lines(layer, draw, lines, font, y)
    if preco:
        font = ImageFont.truetype(fp, round(W * 0.06))
        y = _draw_boxed_lines(layer, draw, [preco], font, y, fill=(198, 255, 0, 255))

    # CTA — pill neon na zona de conversão (y~1250..1550 no story)
    if cta:
        font = ImageFont.truetype(fp, round(W * 0.042))
        pill = rounded_pill(cta, font, round(W * 0.035), round(W * 0.02), NEON, PRETO)
        if pill.width > max_w:
            font = ImageFont.truetype(fp, round(W * 0.034))
            pill = rounded_pill(cta, font, round(W * 0.03), round(W * 0.018), NEON, PRETO)
        cta_y = max(y + round(H * 0.04), round(H * 0.68)) if is_story else y + 20
        cta_y = min(cta_y, bottom - pill.height - 20)
        paste_with_shadow(layer, pill, ((W - pill.width) // 2, cta_y), angle=-2.0)

    return layer


# ---------------------------------------------------------------------------
# Modos
# ---------------------------------------------------------------------------

def make_image_story(args, size):
    base = cover_crop(Image.open(args.input), size).convert("RGBA")
    layer = build_text_layer(size, args.headline, args.destaque, args.produto,
                             args.preco, args.cta, not args.sem_logo)
    base.alpha_composite(layer)
    out = base.convert("RGB")
    # story via API: JPEG obrigatório, máx 8MB — reduz qualidade se precisar
    for q in (90, 85, 80, 75, 70):
        out.save(args.output, "JPEG", quality=q, optimize=True)
        if os.path.getsize(args.output) <= 8 * 1024 * 1024:
            break
    print(f"OK: {args.output} ({size[0]}x{size[1]}, {os.path.getsize(args.output) // 1024} KB)")


def make_overlay(args, size):
    layer = build_text_layer(size, args.headline, args.destaque, args.produto,
                             args.preco, args.cta, not args.sem_logo)
    layer.save(args.output, "PNG")
    print(f"OK: {args.output} ({size[0]}x{size[1]}, overlay PNG)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["image", "overlay"])
    ap.add_argument("--input", help="foto de fundo (obrigatório no mode image)")
    ap.add_argument("--output", required=True)
    ap.add_argument("--formato", default="story", choices=list(FORMATOS))
    ap.add_argument("--headline", default="", help='mensagem principal, ex.: "SUPER PROMOÇÃO"')
    ap.add_argument("--destaque", default="", help='badge neon, ex.: "30%% OFF"')
    ap.add_argument("--produto", default="", help="nome/infos do produto")
    ap.add_argument("--preco", default="", help='ex.: "R$ 179,90"')
    ap.add_argument("--cta", default="", help='chamada final, ex.: "Garanta no link da bio"')
    ap.add_argument("--sem-logo", action="store_true")
    args = ap.parse_args()

    size = FORMATOS[args.formato]
    if args.mode == "image":
        if not args.input:
            sys.exit("--input é obrigatório no mode image")
        make_image_story(args, size)
    else:
        make_overlay(args, size)


if __name__ == "__main__":
    main()
