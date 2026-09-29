# imagic MCP server

**The first photo editor with a built-in MCP server.**

[imagic](https://imagic.ink) is a desktop photo editor for Windows and macOS with AI culling, a full non-destructive editor, and style learning. Its MCP (Model Context Protocol) server is built into the app, so Claude Code, Claude Desktop, Cursor, Codex, GitHub Copilot, or any other MCP client can drive the whole pipeline: scan a shoot, cull it, edit it in your style, and export the keepers. Everything runs locally on your machine.

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

Per-client setup for fourteen clients (config file locations, the right config key for each) is at [imagic.ink/mcp/setup](https://imagic.ink/mcp/setup).

### Claude Code

```bash
claude mcp add imagic -- "C:\Program Files\imagic\imagic.exe" --mcp
```

On macOS:

```bash
claude mcp add imagic -- /Applications/imagic.app/Contents/MacOS/imagic --mcp
```

### Claude Desktop, Cursor and other JSON-config clients

Add this to the client's MCP config (`claude_desktop_config.json` for Claude Desktop):

```json
{
  "mcpServers": {
    "imagic": {
      "command": "C:\Program Files\imagic\imagic.exe",
      "args": ["--mcp"]
    }
  }
}
```

On macOS use `"command": "/Applications/imagic.app/Contents/MacOS/imagic"` with the same `"args": ["--mcp"]`.

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

## The 21 tools

| Tool | What it does | Say this |
|---|---|---|
| `scan_directory` | Index a folder of RAWs and JPEGs into the library. | "Scan D:/Shoots/june-wedding and tell me what's inside." |
| `list_photos` | List photos with their scores, filtered by status, a page at a time. | "List everything you kept in this shoot." |
| `get_photo` | Pull one photo's full record, scores and metadata. | "What did the analysis say about _MG_2041.CR3?" |
| `get_library_stats` | Shoot-level counts, keep rates, and cull progress. | "How far through culling this shoot am I?" |
| `analyze_photos` | Score sharpness, exposure, noise, composition, and detail. Flags duplicates and bursts. | "Score everything and flag the keepers." |
| `set_photo_status` | Override one photo's decision: keep, trash, or back to undecided. Trash never deletes files. | "Keep number 12, trash 15." |
| `reselect_photos` | Re-rank keepers instantly, no re-analysis. Top-N portfolio mode. | "Actually, just keep the best 150." |
| `check_score_freshness` | Report how many stored scores came from an older AI scorer. | "Are any of these scores out of date?" |
| `reanalyze_stale_photos` | Re-score only the photos an older scorer judged; your manual picks are left alone. | "Re-score the stale ones." |
| `apply_adjustments` | Exposure, color, crop, the full adjustment set, per photo or in batch. | "Lift the shadows a touch on the ceremony set." |
| `list_presets` | Every preset saved in your imagic install, listed for the agent. | "What presets do I have to work with?" |
| `apply_preset` | Batch-apply any saved preset across a selection. | "Run my film preset over the golden hour frames." |
| `get_photo_edits` | Read the non-destructive edit stack sitting on any photo. | "What edits are on this file right now?" |
| `start_style_calibration` | Begin the guided calibration on up to 8 photos from your library. | "Let's teach you how I edit." |
| `record_style_calibration` | Save each calibration edit as you make it. | "Done with this one, remember those choices." |
| `get_style_profile` | Inspect what the calibration learned about your taste. | "Describe my editing style back to me." |
| `apply_my_style` | Edit any set of photos the way you would have. | "Edit the whole shoot like I would." |
| `learn_style_from_library` | Train the profile on every photo you've ever edited in imagic. | "Learn my style from everything I have edited." |
| `match_style_from_examples` | Edit a few frames from a shoot; it matches the rest to that look, without touching your saved profile. | "I edited five from this wedding, match the rest to them." |
| `export_photos` | Batch export the keepers in your format and size, resumable if interrupted mid-batch. | "Export the keepers as full-res JPEGs." |
| `get_preview_url` | Link to the local live-preview page that shows what the agent is doing as it happens. | "Show me what you are doing." |

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

The MCP server and headless CLI are part of **imagic Max** (EUR 99, one-time, no subscription). imagic's paid tiers start at EUR 19; Lite and Plus run the full GUI but do not unlock headless or MCP automation. The **free trial includes full Max access** for 500 exports, MCP and CLI included, with no card required.

Headless and MCP use need an activated desktop license: launch the GUI once, activate with your trial or license key, and the MCP server reuses that activation.

## Links

- [imagic.ink/mcp](https://imagic.ink/mcp): full MCP and CLI guide, per-client setup, FAQ
- [imagic.ink/automation](https://imagic.ink/automation): all three automation routes (in-app batch tools, headless CLI, MCP)
- [imagic.ink/desktop](https://imagic.ink/desktop): download and free trial

---

imagic is a closed-source commercial application. This documentation is (c) imagic. You are welcome to reference and link to it, including in MCP directories and registries.
