"""Re-encode generated motion GIF with a shared palette and delta rectangles."""
from PIL import Image,ImageSequence
from pathlib import Path
p=Path(__file__).resolve().parent/'visuals/insertion-removal.gif'
im=Image.open(p);duration=im.info.get('duration',50)
frames=[f.convert('RGB') for f in ImageSequence.Iterator(im)]
palette=frames[0].quantize(colors=128)
frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
frames[0].save(p,save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=True,disposal=1)
print(f'{len(frames)} frames, {p.stat().st_size} bytes')
