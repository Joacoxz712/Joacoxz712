from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageSequence


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "rounded"
OUTPUT.mkdir(parents=True, exist_ok=True)

LOCAL_GIFS = [
    "resource-01.gif",
    "resource-02.gif",
    "resource-05.gif",
    "resource-06.gif",
    "resource-07.gif",
    "resource-09.gif",
    "resource-10.gif",
    "resource-11.gif",
]

REMOTE_GIFS = {
    "sonic.gif": "https://media1.tenor.com/m/Pjo1KC6fRPEAAAAd/sonic.gif",
    "rei.gif": "https://media1.tenor.com/m/WWs67w1IWAUAAAAd/rei-ayanami.gif",
    "kaworu.gif": "https://media1.tenor.com/m/9ByocAJi3EAAAAAd/kaworu-kaworu-nagisa.gif",
}


def load_image(source):
    if isinstance(source, Path):
        return Image.open(source)

    request = Request(
        source,
        headers={"User-Agent": "Mozilla/5.0 (compatible; CocoProfileAssets/1.0)"},
    )
    with urlopen(request, timeout=45) as response:
        return Image.open(BytesIO(response.read()))


def rounded_frames(image):
    frames = []
    durations = []
    scale = 4

    for frame in ImageSequence.Iterator(image):
        rgba = frame.convert("RGBA")
        width, height = rgba.size

        mask = Image.new("L", (width * scale, height * scale), 0)
        draw = ImageDraw.Draw(mask)
        radius = min(24, width // 8, height // 8) * scale
        draw.rounded_rectangle(
            (0, 0, width * scale - 1, height * scale - 1),
            radius=radius,
            fill=255,
        )
        mask = mask.resize((width, height), Image.Resampling.LANCZOS)
        alpha = ImageChops.multiply(rgba.getchannel("A"), mask)
        rgba.putalpha(alpha)

        indexed = rgba.convert("RGB").quantize(
            colors=255,
            method=Image.Quantize.MEDIANCUT,
        )
        transparent = alpha.point(lambda value: 255 if value < 128 else 0)
        indexed.paste(255, mask=transparent)
        indexed.info["transparency"] = 255

        frames.append(indexed)
        durations.append(frame.info.get("duration", image.info.get("duration", 100)))

    return frames, durations


def save_rounded(source, destination):
    image = load_image(source)
    frames, durations = rounded_frames(image)

    if not frames:
        raise RuntimeError(f"No frames found in {source}")

    frames[0].save(
        destination,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=image.info.get("loop", 0),
        disposal=2,
        transparency=255,
        optimize=True,
    )
    image.close()


for filename in LOCAL_GIFS:
    source = ROOT / "assets" / "inspiration" / filename
    save_rounded(source, OUTPUT / filename)

for filename, url in REMOTE_GIFS.items():
    save_rounded(url, OUTPUT / filename)

print(f"Generated {len(LOCAL_GIFS) + len(REMOTE_GIFS)} rounded animated GIFs.")
