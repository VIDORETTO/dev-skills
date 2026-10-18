# 13: Exemplos em texto (para copiar e adaptar)

## Descrições de personagem (`character.description`)

**Realista com figurino (validado):**
> a slim man in his late thirties with fair, lightly weathered skin, a long angular face, high cheekbones, a straight prominent nose, deep-set dark brown eyes under thick dark eyebrows and light stubble; dark brown voluminous curly hair falling over his ears with long sideburns; a brown-green-orange plaid tweed deerstalker hat with front and back brims and ear flaps tied on top with a small dark brown ribbon bow; a matching brown herringbone tweed coat with a short shoulder cape and wide lapels, a tweed waistcoat, a crisp white high-collar shirt and a dark brown knitted silk tie

**Mulher, casual:**
> a woman in her mid twenties with warm olive skin, an oval face, large hazel eyes, thick straight eyebrows, a small rounded nose and full lips with natural pink lipstick; long wavy chestnut hair with curtain bangs falling past her shoulders; small gold hoop earrings; an oversized cream cable-knit sweater and a thin gold necklace

**Personagem estilizado (cross-style):**
> a 3D animated cartoon fox character with bright orange fur, white muzzle and chest, large emerald-green eyes with long lashes, black-tipped pointed ears; wears a small blue denim vest with brass buttons. Keep the stylized 3D animation look on the character while the scene stays photographic

Regras: idade aparente, pele, formato do rosto, olhos, sobrancelhas, nariz, boca e barba; cabelo (cor, textura, volume, comprimento); **cada peça** com cor, padrão e material; acessórios. Evite nomes próprios de pessoas reais.

## `behavior` por segmento (tempos relativos ao início do segmento)

| Situação | Texto |
|---|---|
| Sopro no início | "From 0.5 s to about 1.9 s he does not speak: he blows a long puff of air toward the camera through rounded, pursed lips (an O-shaped exhale) while the handheld camera bobs. From about 2.0 s to 2.7 s his lips are almost closed and still, with only a quiet breath. From 2.7 s he speaks softly with small, barely opened lip movements, exactly as small as the source performer's mouth. Close the lips between phrases." |
| Fala contínua | "He speaks continuously with natural short breaths between words; lips close briefly at pauses." |
| Sai de quadro com giro de câmera | "He speaks, pauses briefly, says the last words, then turns the camera away to his left; as the camera pans he leaves the frame naturally with the camera movement." |
| Entra de quadro | "The camera pans back from the street to his face; he enters the frame from the left edge already speaking, then faces the camera and finishes the sentence, closing his lips at the end." |
| Riso | "At 1.2–2.0 s he laughs with an open-mouth smile and shaking shoulders; no words." |
| Silêncio ouvindo | "He listens silently with lips closed, small nods at 0.8 s and 2.4 s, blinking naturally." |
| Voz em off | (`speaker: offscreen`) "His lips stay closed; the voice is offscreen narration." |
| Mastigando ou bebendo | "From 3.0 s he takes a sip from the cup; mouth on the rim, then swallows; no speech." |

## Prompt montado pelo `run_job.py` (segmento A1, validado com correlação 0,75)

```
From the very first frame, replace only the selected person in <Video 1> with the single character in <Picture 1>: <DESCRIÇÃO>.
Keep the reference identity and costume, complete and uncropped, throughout. Match source posture, gaze, blinks, facial emotion,
mouth movement, breathing, head movement and camera movement. The selected character is speaking in Portuguese.
Current segment dialogue: <d>[Portuguese] Pessoal, meu nome é Sherlock Holmes.</d> Follow source audio timing exactly; mouth shapes
follow the syllables of <Audio 1>, lips close or relax during silence. Earlier reference dialogue is context only; do not repeat it.
<BEHAVIOR DO SOPRO>. <Audio 1> and source video determine exact timing. Do not repeat earlier dialogue or invent words, gestures,
people or camera cuts. Adapt lighting to the lighting of <Video 1>. Retain the scene outside the person region. Output the raw decoded generation.
```

A continuação acrescenta, depois da descrição: "<Picture 2> is the generated boundary from the preceding segment. Continue its motion and appearance."

## Trecho de `job.json` (formato)

```json
{
 "canvas": {"resolution": "768", "width": 736, "height": 1344},
 "character": {"image": "C:/.../character.png", "description": "..."},
 "settings": {"expansion_px": 144, "lora": "h3_character_swap_v1.5.safetensors", "turbo": true, "steps": 8,
              "sam_text": "person", "selection": "largest", "language": "Portuguese", "use_anchor": false},
 "shots": [
  {"id": "A", "mode": "generate", "start": 0, "end": 372, "segments": [
    {"id": "A1", "start": 0, "end": 130, "history": 0, "window": 141, "dialogue": "Pessoal, meu nome é Sherlock Holmes.",
     "speaker": "target", "nonverbal": [{"t0": 0.5, "t1": 1.9, "type": "vocal_nonspeech", "label": "sopro"}],
     "behavior": "From 0.5 s to about 1.9 s ...", "seed": 31337, "selected_take": "A1_s31337", "clip": "clips/A1.mp4"},
    {"id": "A2", "start": 130, "end": 283, "history": 18, "window": 158, "dialogue": "Eu passei 5 anos procurando ...",
     "speaker": "target", "behavior": "He speaks continuously ...", "seed": 904240, "clip": "clips/A2.mp4"}]},
  {"id": "B", "mode": "preserve", "start": 372, "end": 442},
  {"id": "C", "mode": "generate", "start": 442, "end": 540, "segments": [ ... ]}]
}
```

## Relatórios ao usuário

**Prévio:** ver o modelo em [00-analise-previa.md](00-analise-previa.md).

**Entrega:**
> Pronto: `final.mp4` (736x1344, 22,5 s, áudio original). Lip sync: A 0,71 · C 0,82 (atraso 0). Chapéu inteiro em todos os closes; fachada original (sem personagem); cor idêntica à fonte. Ponto fraco: "Pessoal" (3–4 s) com boca mais articulada que a sua; 5 variações testadas, limite conhecido do LoRA. Custo ~US$ 3,30; RunPod zerado.
