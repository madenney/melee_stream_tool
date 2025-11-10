use std::{
  fs,
  path::PathBuf,
  sync::{Arc, Mutex},
};

use tauri::{Manager, State as TauriState};

mod model;
use model::*;

use axum::{
  extract::State as AxumState,
  response::IntoResponse,
  routing::{get, get_service},
  Router,
};
use tokio::net::TcpListener;
use tower_http::services::ServeDir;

/// Shared store (used by Tauri commands and the Axum server)
struct InnerStore {
  overlay_dir: PathBuf,
  state_path: PathBuf,
  state: Mutex<OverlayState>,
}
type Store = Arc<InnerStore>;

fn default_state() -> OverlayState {
  OverlayState {
    p1: PlayerState {
      side: "left".into(),
      port: Some(1),
      tag: "Player 1".into(),
      sponsor: None,
      handle: None,
      character: "Falco".into(),
      character_color: "Blue".into(),
      score: 0,
      country_code: None,
    },
    p2: PlayerState {
      side: "right".into(),
      port: Some(2),
      tag: "Player 2".into(),
      sponsor: None,
      handle: None,
      character: "Marth".into(),
      character_color: "Red".into(),
      score: 0,
      country_code: None,
    },
    meta: MatchMeta {
      tournament: Some("Melee Local".into()),
      round: "WF".into(),
      best_of: 5,
      game_number: Some(1),
      stage: None,
      notes: None,
    },
    commentators: vec![],
  }
}


fn read_state(path: &PathBuf) -> OverlayState {
  match fs::read_to_string(path) {
    Ok(s) => serde_json::from_str(&s).unwrap_or_else(|_| default_state()),
    Err(_) => default_state(),
  }
}

fn write_state(path: &PathBuf, s: &OverlayState) -> Result<(), String> {
  if let Some(parent) = path.parent() {
    fs::create_dir_all(parent).map_err(|e| e.to_string())?;
  }
  fs::write(path, serde_json::to_string_pretty(s).unwrap()).map_err(|e| e.to_string())
}

#[tauri::command]
fn get_state(store: TauriState<Store>) -> OverlayState {
  store.state.lock().unwrap().clone()
}

#[tauri::command]
fn update_state(store: TauriState<Store>, new_state: OverlayState) -> Result<(), String> {
  if new_state.meta.best_of != 3 && new_state.meta.best_of != 5 {
    return Err("bestOf must be 3 or 5".into());
  }
  *store.state.lock().unwrap() = new_state.clone();
  write_state(&store.state_path, &new_state)
}

#[tauri::command]
fn swap_sides(store: TauriState<Store>) -> Result<OverlayState, String> {
  let mut st = store.state.lock().unwrap();

  // Safe swap via clone to satisfy the borrow checker
  let tmp = st.p1.clone();
  st.p1 = st.p2.clone();
  st.p2 = tmp;

  // Normalize sides after swap
  st.p1.side = "left".into();
  st.p2.side = "right".into();

  write_state(&store.state_path, &st)?;
  Ok(st.clone())
}

#[tokio::main(flavor = "multi_thread")]
async fn main() {
  tauri::Builder::default()
    .setup(|app| {
      // Serve from project root: ../overlay next to repo root
      // current_dir() when launched from src-tauri is ".../melee_stream_tool/src-tauri"
      let overlay_dir = std::env::current_dir()
        .unwrap()
        .parent().unwrap()            // up to project root
        .to_path_buf()
        .join("overlay");

      let state_path = overlay_dir.join("state.json");

      // Ensure overlay dir exists and there is a state.json
      fs::create_dir_all(&overlay_dir).ok();
      if !state_path.exists() {
        let _ = write_state(&state_path, &default_state());
      }
      let initial = read_state(&state_path);

      let store: Store = Arc::new(InnerStore {
        overlay_dir: overlay_dir.clone(),
        state_path: state_path.clone(),
        state: Mutex::new(initial),
      });

      // Expose to Tauri commands
      app.manage(store.clone());

      // Start the embedded HTTP server for OBS
      tokio::spawn(start_server(store));

      println!("Serving overlay dir: {}", overlay_dir.display());
      println!("State file: {}", state_path.display());

      Ok(())
    })
    .invoke_handler(tauri::generate_handler![get_state, update_state, swap_sides])
    .run(tauri::generate_context!())
    .expect("error while running tauri app");
}

async fn start_server(store: Store) {
  // Serve static files from ./overlay at /
  let files = get_service(ServeDir::new(store.overlay_dir.clone()));

  // Router:
  //   /state.json -> current overlay state (no-cache)
  //   /           -> static files (index.html, style.css, icons, etc.)
  let app = Router::new()
    .route(
      "/state.json",
      get({
        let store = store.clone();
        move || get_state_json(AxumState(store))
      }),
    )
    .nest_service("/", files);

  let addr = "127.0.0.1:17890";
  let listener = TcpListener::bind(addr).await.expect("bind 17890");
  println!("Overlay server at http://{addr}/ (open /index.html)");
  axum::serve(listener, app).await.expect("serve axum");
}

async fn get_state_json(AxumState(store): AxumState<Store>) -> impl IntoResponse {
  let s = store.state.lock().unwrap().clone();
  let body = serde_json::to_string(&s).unwrap();
  (
    [
      ("Content-Type", "application/json"),
      ("Cache-Control", "no-store"),
      ("Pragma", "no-cache"),
      ("Expires", "0"),
    ],
    body,
  )
}
