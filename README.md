# markdown-records-media

Public media for MARKDOWN Records. Only content that is (or is about to be) public lives here.

- `published/`: approved pieces, named `MD_[platform]_[type]_[ratio]_vNN`. Their raw URLs feed Metricool.
- `assets/backgrounds/`: AI-generated backgrounds (no logo, no text).
- `assets/videos/`: animated backgrounds and tests.
- `brand/`: logo master (SVG) and fonts (Space Grotesk, IBM Plex Mono).
- `templates/`: composition scripts. Run from the repo root.
  - `compose_statement.py`: 4:5 statement piece (logo as signature, Space Grotesk + IBM Plex Mono). Needs Pillow.
  - `pulse_beat.py`: beat-locked edge pulse over a still (144 BPM, 24 fps, 10 frames per beat). Needs numpy, Pillow, ffmpeg.
  - `compose.py`: parametrized feed (4:5) / story (9:16) composer: text + logo signature over a clean background. Single piece via flags or several (carousel, 3-story set) via `--spec spec.json`. Text auto-fits, story safe zones respected.
  - `pulse.py`: parametrized `pulse_beat.py` (`--bg --out --bpm --seconds`).
  - `overlay_video.py`: burns static text + logo over a clean clip (pulse.py or a Krea video).
  - `mdlib.py`: shared helpers (logo geometry, fonts, layout). Backgrounds and clips never contain text or logo; all text/logo is added by these scripts.
