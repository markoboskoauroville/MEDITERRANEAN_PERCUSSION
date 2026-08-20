#!/usr/bin/env python3
"""Paint the plates for the field book. One style paragraph, varied only by scene."""
import json, base64, os, sys, time, urllib.request

KEY = open('/home/claude/.secret/gemini_key').read().strip()
URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
       "gemini-3-pro-image-preview:generateContent")
OUT = '/home/claude/MEDITERRANEAN_PERCUSSION/images'

STYLE = (
    "Dark moody watercolour on textured paper, in the manner of a nocturne. "
    "One warm amber light source glowing from inside the composition; everything else "
    "deep umber, warm black and soft indigo shadow. Loose wet brushwork, visible paper "
    "grain, soft bleeding edges. Silhouettes and suggestion rather than detail. "
    "Intimate, quiet, hand-painted. The painting fills the entire frame edge to edge "
    "with no white paper border, no margin and no mount. "
    "Absolutely no text, no letters, no words, no numbers, no symbols, no interface "
    "elements and no signature anywhere in the image. SCENE: "
)

SCENES = {
 "00_hero": "a large round frame drum resting across a seated person's knee in a dark bare room, one small amber lamp on the floor beside it, the player only a silhouette",
 "01_relief": "a broken fragment of carved stone relief showing a hand holding a round drum, warm amber light raking across the carving from one side",
 "02_stage": "a single round frame drum standing upright alone in the centre of a completely empty dark stage under one warm amber spotlight",
 "03_circle": "a ring of round frame drums laid flat on dark earth, one of them lit warm amber from above, the others in deep shadow",
 "04_workshop": "a drum maker's workbench at night, a skin stretched over a wooden hoop, tools and shavings, one amber lamp",
 "05_lamps": "one bright amber lamp at the centre of a dark space with many smaller amber lamps arranged in a wide circle far around it",
 "06_hand": "a single human hand caught in motion just above a taut drum skin, the fingers blurred with movement, warm amber light raking low across the surface",
 "07_drums": "several round frame drums of different sizes leaning against a dark wall, warm amber light falling across their pale skins",
 "08_stones": "a row of smooth stones of different sizes laid out on dark ground, warm amber light picking out the larger ones more brightly",
 "09_daf": "a large round frame drum held up in darkness, warm amber light glowing through the translucent skin from behind it",
 "10_goblet": "the dark silhouette of a tall goblet shaped drum standing beside a low amber fire, suggestions of seated figures in the darkness beyond",
 "11_small": "one very small round hand drum lying alone on dark folded cloth on a table, seen from above, warm amber light from one side, no people, no hands, no figures",
 "12_doorway": "an open doorway at night with round frame drums hanging on the wall inside, warm amber light spilling out across a dark stone floor",
}

def paint(name, scene, retries=3):
    body = json.dumps({
        "contents": [{"parts": [{"text": STYLE + scene}]}],
        "generationConfig": {"responseModalities": ["IMAGE"],
                             "imageConfig": {"aspectRatio": "16:9"}},
    }).encode()
    for attempt in range(retries):
        req = urllib.request.Request(URL, data=body, headers={
            "x-goog-api-key": KEY, "Content-Type": "application/json",
            "User-Agent": "mantra-field-books/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.load(r)
        except urllib.error.HTTPError as e:
            code = e.code
            if code == 429:                      # valid key, throttled — rest it
                time.sleep(20 * (attempt + 1)); continue
            print(f"  {name}: HTTP {code}"); return False
        for p in d["candidates"][0]["content"]["parts"]:
            if "inlineData" in p:
                raw = base64.b64decode(p["inlineData"]["data"])
                open(f"{OUT}/{name}.jpg", "wb").write(raw)
                print(f"  {name}: {len(raw)//1024} KB")
                return True
        print(f"  {name}: no image part returned"); time.sleep(5)
    return False

if __name__ == "__main__":
    want = sys.argv[1:] or list(SCENES)
    ok = 0
    for n in want:
        if os.path.exists(f"{OUT}/{n}.jpg"):
            print(f"  {n}: already painted, skipping"); ok += 1; continue
        if paint(n, SCENES[n]): ok += 1
        time.sleep(2)
    print(f"painted {ok}/{len(want)}")
