# markdown-records-media

Public media for MARKDOWN Records. Only content that is (or is about to be) public lives here.

- `published/`: approved pieces, named `MD_[platform]_[type]_[ratio]_vNN`. Their raw URLs feed Metricool.
- `semanas/AAAA-Wnn/`: pieces rendered by the content system (markdown-records, `content/scripts/render.py`). Written only by the render workflow; their raw URLs feed Metricool and the Telegram bot.
- `assets/backgrounds/`: AI-generated backgrounds (no logo, no text).
- `assets/videos/`: animated backgrounds (`pulse_*` loops are the reusable pool) and tests. `test_kling3_*` stays out of the pool: Kling commercial licence not confirmed.
- `brand/`: logo master (SVG) and fonts (Space Grotesk, IBM Plex Mono).
- `templates/`: composition scripts. Run from the repo root.
  - `compose.py`: parametrized feed (4:5) / story (9:16) composer: text + logo signature over a clean background. Single piece via flags or several (carousel, 3-story set) via `--spec spec.json`. Text auto-fits, story safe zones respected.
  - `pulse.py`: beat-locked edge pulse over a still (`--bg --out --bpm --seconds`; default 144 BPM). Needs numpy, Pillow, ffmpeg.
  - `overlay_video.py`: burns static text + logo over a clean clip (pulse.py or a Krea video).
  - `splash.py`: Saturday "Splash" story (content system #55): .MD logo as a title screen and a short message below it, straight and static, over a loop repeated to `--seconds` (720x1280 mp4).
  - `mdlib.py`: shared helpers (logo geometry, fonts, layout). Backgrounds and clips never contain text or logo; all text/logo is added by these scripts.
