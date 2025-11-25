# Melee Stream Tool

Tauri + React desktop helper for running multiple Melee stream overlays from one machine. It manages a shared state file and serves browser sources for OBS: single, upcoming, dual, and quad overlays.

## Quick start
- Install deps: `npm install`
- Run the app + overlay servers: `npm run tauri dev` (or `npm run dev` for the React UI only)
- OBS Browser Sources:
  - Main: `http://127.0.0.1:17890/`
  - Upcoming: `http://127.0.0.1:17891/`
  - Dual (setups 1–2 side by side): `http://127.0.0.1:17892/`
  - Quad (setups 1–4 grid): `http://127.0.0.1:17893/`
  - You can target a specific setup on main/upcoming with `?setup=N` (1–4). Default is setup 1.

## State model
- Stored at `overlay/state.json`.
- Multi-setup format:
  ```json
  {
    "setups": [ { /* setup 1 */ }, { /* setup 2 */ }, { /* setup 3 */ }, { /* setup 4 */ } ]
  }
  ```
- Each setup has `p1`, `p2`, `meta`, `commentators` (same fields as before). `bestOf` must be 3 or 5. Legacy single-state files are auto-wrapped into this format and the remaining slots are filled with defaults.

## Editor (desktop app)
- UI lives at `http://localhost:1420/` during `tauri dev`.
- Top-left selector chooses which setup (1–4) you’re editing; save writes the whole `setups` array to disk.
- “Swap Sides” targets the selected setup.
- Character/color dropdowns auto-adjust colors per character; names shrink to fit in the overlay boxes.

## Overlays
- Main overlay: `overlay/index.html` pulls `/state.json` and supports `?setup=N`.
- Upcoming overlay: `overlay/upcoming/index.html` (faceoff view) also supports `?setup=N`.
- Dual/Quad overlays: `overlay/dual` and `overlay/quad` embed the main overlay for setups 1–2 and 1–4 respectively (scaled via CSS). Served on ports 17892/17893.
- Shared assets (portraits, etc.) live under `overlay/resources/`.

## Notes
- Servers run on localhost; if you need to expose externally, put them behind a reverse proxy (see `notes/server_files/nginx_config` for an example OME/WHIP + web proxy setup).
- The overlay servers are started by the Tauri backend; if you only run the Vite dev server, the OBS URLs above won’t be available.***
