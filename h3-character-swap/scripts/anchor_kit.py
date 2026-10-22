"""Pacote para o USUÁRIO fazer a âncora num editor de imagem externo (Nano Banana / Gemini, GPT Image / ChatGPT),
em vez de gerar com o Qwen-Image-Edit no pod. Roda antes de criar o pod (só stdlib + ffmpeg).

Uso: python anchor_kit.py JOB.json <shot|seg> [<shot|seg> ...]
Gera em JOB/anchor_kit/:
  <id>_frame.png        o frame a editar (1º frame do shot/segmento, no recorte do vídeo final, na resolução da fonte)
  personagem.<ext>      a imagem de referência do personagem (e personagem_extra.<ext>, se houver)
  PROMPT_<id>.txt       o prompt pronto para colar (em inglês: os dois editores seguem melhor)
  COMO_FAZER.md         o passo a passo para o usuário, em português
  ENTREGA.md            o que o agente entrega na conversa: caminhos dos arquivos a anexar + o prompt completo
                        (o mesmo texto é impresso no terminal)
e cria JOB/anchors_user/, onde as imagens editadas devem voltar como <id>_v1.png, <id>_v2.png…
Depois: VPY S/qa_anchor.py JOB.json <id> --set  (alinha ao frame original, mede, cola de volta e escolhe a melhor)
"""
import os, shutil, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3common import load_job, ensure_frame


def brief(desc):
    return (
        "Edit Image 1. Image 2 shows the character's identity only.\n\n"
        f"Replace ONLY the main person in Image 1 with the character from Image 2: {desc}.\n\n"
        "Keep EVERYTHING else from Image 1 exactly the same: the same camera framing and crop, the same image size and "
        "aspect ratio, the same background, objects, lighting, colors and grain. Do not zoom in or out, do not move "
        "the camera, do not extend or crop the image, do not add any other person. If you cannot keep this aspect "
        "ratio, add plain borders around the whole image instead of cropping it.\n\n"
        "The character must take the exact place of the original person: same position and size in the frame, same "
        "head size and tilt, same face angle and gaze, same body pose and hand positions, and the same mouth opening "
        "and lip shape as in Image 1 (if the mouth is slightly open mid-word, keep it slightly open). Anything cut by "
        "the frame edge stays cut the same way.\n\n"
        "Keep the character's face, hair and full costume from Image 2, but lit by the light of Image 1 (not studio "
        "light). Do not copy the pose, background or framing of Image 2.\n\n"
        "Output: one photorealistic image that looks like a real frame of the same video."
    )


HOWTO = """# Como fazer a âncora você mesmo

A âncora é o **primeiro frame do vídeo já com o personagem no lugar da pessoa**. Ela orienta o início da geração.
Ela só ajuda se parecer **um frame real do próprio vídeo**: mesmo enquadramento, mesma escala, mesma pose e **mesma
abertura de boca**. Uma âncora "bonita" mas reenquadrada piora o resultado (no caso Sherlock, derrubou o lip sync).

## Arquivos deste pacote

{files}

## Passo a passo

1. Abra o editor:
   - **Nano Banana:** no app/site do Gemini (ou no Google AI Studio), escolha o modelo de imagem Nano Banana.
   - **GPT Image:** no ChatGPT, peça uma edição de imagem.
2. Anexe **duas imagens, nesta ordem**: primeiro o frame (`<id>_frame.png`), depois o personagem (`personagem.*`).
3. Cole o texto do `PROMPT_<id>.txt` correspondente, sem mudar nada.
4. Gere **2 a 4 variações**. Descarte na hora as que:
   - afastaram ou aproximaram a câmera, cortaram ou aumentaram a imagem;
   - mudaram a pose, o lugar da pessoa ou a boca (aberta/fechada diferente do frame original);
   - mudaram o fundo ou inventaram outra pessoa.
5. Baixe as que sobraram **na maior resolução disponível, em PNG**, sem recortar.
   - Se o editor devolver em outro formato (o GPT Image costuma devolver 2:3 em vez de 9:16), tudo bem: a skill alinha
     a imagem ao frame original. Só não recorte você mesmo.
   - Confira se o editor **não cortou** a cabeça, os pés ou as laterais da pessoa. O prompt pede bordas em vez de
     recorte; se mesmo assim cortar, gere outra variação (a parte cortada ficaria com a pessoa original).
6. Devolva as imagens:
   - salve em `{back}` com os nomes `<id>_v1.png`, `<id>_v2.png`…; **ou**
   - anexe aqui no chat dizendo de qual shot é cada uma.

Depois disso a IA mede cada variação (enquadramento, escala do rosto, boca, identidade, nitidez, pessoa extra ou
cortada), confere visualmente costura, mãos, restos da pessoa original, figurino e luz, cola o personagem de volta
sobre o frame original para o fundo ficar idêntico e diz qual variação aprovou. Se nenhuma passar, ela explica o
motivo e te dá a frase exata para pedir a correção no mesmo chat do editor; ou vocês seguem sem âncora.

## Avisos

- Você vai enviar frames do seu vídeo e a imagem do personagem para o Google ou a OpenAI. Se o vídeo for privado,
  considere isso; a outra opção é a IA gerar com o Qwen no próprio pod.
- Esses editores podem recusar edições com fotos de pessoas reais. Se recusarem, a outra opção é o Qwen no pod.
- Shot em que a pessoa entra pela borda do quadro no primeiro frame: **não faça âncora** para ele.
"""


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    job = load_job(sys.argv[1]); D = job["_dir"]
    kit = os.path.join(D, "anchor_kit"); back = os.path.join(D, "anchors_user")
    os.makedirs(kit, exist_ok=True); os.makedirs(back, exist_ok=True)
    ch = job["character"]
    desc = ch["description"]
    if desc.startswith("PREENCHER"):
        raise SystemExit("Preencha character.description no job.json antes: ele entra no prompt.")
    files = []
    for key, name in [("image", "personagem"), ("extra_image", "personagem_extra")]:
        if ch.get(key):
            src = ch[key] if os.path.isabs(ch[key]) else os.path.join(D, ch[key])
            dst = os.path.join(kit, name + os.path.splitext(src)[1].lower())
            shutil.copyfile(src, dst); files.append(dst)
    for item in sys.argv[2:]:
        ensure_frame(job, item)                               # frame no canvas (referência do qa_anchor)
        files.append(ensure_frame(job, item, full_res=True))  # frame para o editor externo
        p = os.path.join(kit, f"PROMPT_{item}.txt")
        open(p, "w", encoding="utf-8").write(brief(desc) + "\n"); files.append(p)
    listing = "\n".join(f"- `{os.path.basename(f)}`" for f in files)
    open(os.path.join(kit, "COMO_FAZER.md"), "w", encoding="utf-8").write(
        HOWTO.format(files=listing, back=os.path.relpath(back, D) + "/"))
    # Bloco de ENTREGA: o agente envia estes arquivos ao usuário (anexo/cartão de arquivo do host) e cola o prompt
    # no chat. Também fica salvo em ENTREGA.md.
    imgs = [f for f in files if not f.endswith(".txt")]
    lines = ["# Entrega ao usuário: âncora de 1º frame", "",
             "Arquivos para ENVIAR ao usuário (anexar na conversa):"]
    lines += [f"- {os.path.abspath(f)}" for f in imgs]
    for item in sys.argv[2:]:
        lines += ["", f"## Shot/segmento {item}", "",
                  f"Anexe no editor, nesta ordem: 1) `{item}_frame.png`  2) `personagem` "
                  "(e `personagem_extra`, se houver). Cole este prompt sem mudar nada:", "", "```text", brief(desc), "```",
                  "", f"Devolva 2–4 variações como `{item}_v1.png`, `{item}_v2.png`… (PNG, resolução máxima, sem recortar)."]
    lines += ["", f"Pasta de retorno: {os.path.abspath(back)}",
              f"Depois do retorno: VPY S/qa_anchor.py {sys.argv[1]} <id> --set  (e abrir a folha de revisão que ele gera)"]
    text = "\n".join(lines)
    open(os.path.join(kit, "ENTREGA.md"), "w", encoding="utf-8").write(text + "\n")
    print(text)
    print(f"\n(passo a passo completo para o usuário: {os.path.abspath(os.path.join(kit, 'COMO_FAZER.md'))})")


if __name__ == "__main__":
    main()
