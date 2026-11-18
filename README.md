# imagic MCP server

**The first photo editor with a built-in MCP server.**

[imagic](https://imagic.ink) is a desktop photo editor for Windows, macOS and Linux (portable build) with AI culling, a full non-destructive editor, and style learning. Its MCP (Model Context Protocol) server is built into the app, so Claude Code, Claude Desktop, Cursor, Codex, GitHub Copilot, or any other MCP client can drive the whole pipeline: scan a shoot, cull it, edit it in your style, and export the keepers. Everything runs locally on your machine.

This repository is the documentation and setup reference for that server. The server itself ships inside the imagic desktop app; there is no separate server source here.

- Full guide: [imagic.ink/mcp](https://imagic.ink/mcp)
- Scripting without an AI client: [imagic.ink/automation](https://imagic.ink/automation)
- Download: [imagic.ink/desktop](https://imagic.ink/desktop)

## What an agent can do with it

Once connected, the agent calls the same actions you would trigger by hand in the app. Things you can actually say:

- "Scan D:/Shoots/june-wedding, cull it, and tell me what you kept and why."
- "Make the keepers warmer and export them to D:/delivery."
- "Run my film preset over the golden hour frames."
- "Edit the whole shoot like I would." (after style calibration)
- "I edited five from this wedding, match the rest to them."
- "Actually, just keep the best 60 for the client gallery." (instant re-rank, no re-analysis)
- "Export the keepers as full-res JPEGs."

Edits land as non-destructive adjustments in imagic's edit history, the same as manual edits. Nothing overwrites your originals unless you explicitly export.

## Install

1. Download imagic from [imagic.ink/desktop](https://imagic.ink/desktop). The free trial covers 500 exports with everything in imagic Max, no card required (importing, culling and editing never count against it).
2. Launch the app once and activate (trial or license). The MCP server reuses that activation.
3. Connect your MCP client (below).

The server is the imagic app itself, started with `--mcp`. There is no pip package and no separate `imagic-mcp` command in the packaged app; point your client at the installed binary:

- Windows: `C:\Program Files\imagic\imagic.exe`
- macOS: `/Applications/imagic.app/Contents/MacOS/imagic`
- Linux (portable build): `/path/to/imagic/imagic`, inside the folder you extracted the `.tar.gz` to

**Not our npm package.** The npm package called `imagic-mcp` (run with `npx imagic-mcp`) is an unrelated project by another author. Do not install it to connect imagic. imagic's MCP server is built into the desktop app.

Per-client setup for fourteen clients (config file locations, the right config key for each) is at [imagic.ink/mcp/setup](https://imagic.ink/mcp/setup).

### Claude Code

```bash
claude mcp add imagic -- "C:\Program Files\imagic\imagic.exe" --mcp
```

On macOS:

```bash
claude mcp add imagic -- /Applications/imagic.app/Contents/MacOS/imagic --mcp
```

On Linux:

```bash
claude mcp add imagic -- /path/to/imagic/imagic --mcp
```

### Claude Desktop, Cursor and other JSON-config clients

Add this to the client's MCP config (`claude_desktop_config.json` for Claude Desktop):

```json
{
  "mcpServers": {
    "imagic": {
      "command": "C:\\Program Files\\imagic\\imagic.exe",
      "args": ["--mcp"]
    }
  }
}
```

On macOS use `"command": "/Applications/imagic.app/Contents/MacOS/imagic"` and on Linux `"command": "/path/to/imagic/imagic"`, in both cases with the same `"args": ["--mcp"]`.

### Codex CLI

```bash
codex mcp add imagic -- "C:\Program Files\imagic\imagic.exe" --mcp
```

Or in `~/.codex/config.toml`:

```toml
[mcp_servers.imagic]
command = 'C:\Program Files\imagic\imagic.exe'
args = ["--mcp"]
```

GitHub Copilot and any other MCP-compatible client work the same way: a local stdio server whose command is the imagic binary with `--mcp`.

If you run imagic from a source checkout (developers only, not the packaged app), the checkout's own entry point is `imagic-mcp`, installed from that checkout, never from npm.

## Container and directory listing (introspection only)

The `Dockerfile` in this repository builds a stand-in server for MCP directories such as Glama. It is not the real server and it does no photo work. It starts over stdio, answers `initialize` and `tools/list` with the real imagic tool names, descriptions and input schemas (snapshotted in `tools.json` from the shipping server, version 1.6.1), and answers every `tools/call` with an error saying the imagic desktop app is required. The real server needs the desktop app and your local photo library, so it cannot run in a container. To actually use the tools, install the app as described above.

`tools.json` is the complete list of 30 tools, dumped from the real 1.6.1 server.

```bash
docker build -t imagic-mcp .
python test_introspection.py docker run -i --rm imagic-mcp
```

## The 30 tools

Generated from the tool descriptions the 1.6.1 server itself reports.

| Tool | What it does |
|---|---|
| `scan_directory` | Scan a folder of photos into the imagic library. |
| `analyze_photos` | Run AI quality scoring and auto-culling on all pending photos. |
| `reselect_photos` | Instantly re-rank analysed photos from their stored scores. |
| `check_score_freshness` | Check whether stored quality scores came from the current AI scorer. |
| `reanalyze_stale_photos` | Re-score photos whose stored scores came from an older AI scorer. |
| `get_library_stats` | Get photo counts per pipeline status (pending, keep, trash, ...). |
| `list_photos` | List photos with id, filename, path, status, score, description and capture time. |
| `get_photo` | Get full details for one photo: status, scores, EXIF, edit state. |
| `set_photo_status` | Override a photo's cull decision: pending, keep, trash, or culled. |
| `list_presets` | List available looks: the user's saved presets, scene presets, color grades and experimental presets. |
| `apply_preset` | Apply a saved preset, scene preset, color grade or experimental preset to the given photos. |
| `list_luts` | List the colour LUTs in the user's imagic library. |
| `apply_lut` | Put one of the user's LUTs (see list_luts) on the given photos. |
| `apply_auto_color` | Auto Color: per-channel levels plus colour-cast removal, measured on each photo. |
| `harmonize_series` | Match exposure and white balance between neighbouring photos (drone mosaics, timelapse, events). |
| `preview_mosaic` | Write a PNG preview of a drone set laid out by GPS, before and/or after harmonize_series. |
| `apply_adjustments` | Set editor slider values on one photo, or the same values on several. |
| `mask_adjust` | Mask part of a photo (subject, sky, people or background) and adjust only that part (local adjustments). |
| `crop_photo` | Crop photos to an aspect ratio; imagic does the pixel maths. |
| `save_preset` | Save a photo's current look as a named preset the user can reuse. |
| `export_photos` | Render and export photos with all their edits to a folder. |
| `get_photo_edits` | Read back a photo's current adjustments and edit state. |
| `start_style_calibration` | Begin teaching imagic the user's personal editing style. |
| `record_style_calibration` | Record the user's calibration edits into their style profile. |
| `learn_style_from_library` | Train the user's style profile from photos already edited in imagic. |
| `match_style_from_examples` | Copy the look of a few edited photos onto the rest of a shoot. |
| `get_style_profile` | Get the user's learned style profile, if one exists. |
| `apply_my_style` | Apply the user's learned personal style to the given photos. |
| `get_preview_url` | Get the local live-preview URL showing your edits in real time. |
| `get_job_status` | Check on a long-running job started by another tool on a remote connection. |

## Style learning: start with 8, train it on everything

imagic's style tools are what make agent-driven editing personal rather than generic:

1. **A guided start, 8 photos.** `start_style_calibration` pulls up to 8 scenario photos from your own library, covering a spread of light and subjects. Edit them your way in imagic, `record_style_calibration` saves each decision, and you have a first profile in minutes.
2. **It reads your real decisions.** The actual exposure, color, and crop values you set in imagic, recorded per scenario and turned into a profile that is yours alone. Inspect it any time with `get_style_profile`.
3. **Then train it on everything.** Repeat sessions whenever your taste shifts, or point `learn_style_from_library` at your back catalog: every photo you have ever edited in imagic feeds the profile. `apply_my_style` then edits any future shoot the way you would have.

Within a single shoot there is also edit-five-match-the-rest: hand-edit a few frames, then `match_style_from_examples` matches the remaining photos to that look without changing your saved profile.

The honest boundary: it learns from edits made in imagic, reading the actual adjustment values you set. It cannot guess your style from exported JPEGs or a Lightroom catalog.

## Privacy

The MCP server runs locally beside imagic and talks to your AI client over your own machine. The agent sends tool calls and instructions; your photos are never uploaded anywhere. All scanning, scoring, editing, and exporting happens on your hardware, the same as using imagic directly.

## Licensing

This repository (the introspection server, tool list and docs) is MIT licensed, see LICENSE. The imagic desktop app it drives is separate, proprietary software that needs its own trial or licence from https://imagic.ink.

The MCP server and headless CLI are part of **imagic Max** (EUR 99, one-time, no subscription). imagic's paid tiers start at EUR 19; Lite and Plus run the full GUI but do not unlock headless or MCP automation. The **free trial includes full Max access** for 500 exports, MCP and CLI included, with no card required.

Headless and MCP use need an activated desktop license: launch the GUI once, activate with your trial or license key, and the MCP server reuses that activation.

## Links

- [imagic.ink/mcp](https://imagic.ink/mcp): full MCP and CLI guide, per-client setup, FAQ
- [imagic.ink/automation](https://imagic.ink/automation): all three automation routes (in-app batch tools, headless CLI, MCP)
- [imagic.ink/desktop](https://imagic.ink/desktop): download and free trial

---

imagic is a closed-source commercial application. This documentation is (c) imagic. You are welcome to reference and link to it, including in MCP directories and registries.
