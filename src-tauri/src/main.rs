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
  state_path: PathBuf,
  state: Mutex<AllSetupsState>,
}
type Store = Arc<InnerStore>;

fn default_setup() -> OverlayState {
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

fn default_state() -> AllSetupsState {
  AllSetupsState {
    setups: (0..4).map(|_| default_setup()).collect(),
  }
}

fn read_state(path: &PathBuf) -> AllSetupsState {
  match fs::read_to_string(path) {
    Ok(s) => {
      // Try multi-setup first
      if let Ok(all) = serde_json::from_str::<AllSetupsState>(&s) {
        return all;
      }
      // Fallback: legacy single setup -> wrap into multi
      if let Ok(single) = serde_json::from_str::<OverlayState>(&s) {
        let mut setups = vec![single];
        // fill the rest with defaults to 4 setups
        while setups.len() < 4 {
          setups.push(default_setup());
        }
        return AllSetupsState { setups };
      }
      default_state()
    }
    Err(_) => default_state(),
  }
}

fn write_state(path: &PathBuf, s: &AllSetupsState) -> Result<(), String> {
  if let Some(parent) = path.parent() {
    fs::create_dir_all(parent).map_err(|e| e.to_string())?;
  }
  fs::write(path, serde_json::to_string_pretty(s).unwrap()).map_err(|e| e.to_string())
}

#[tauri::command]
fn get_state(store: TauriState<Store>) -> AllSetupsState {
  store.state.lock().unwrap().clone()
}

#[allow(non_snake_case)]
#[tauri::command]
fn update_state(store: TauriState<Store>, newState: AllSetupsState) -> Result<AllSetupsState, String> {
  println!(
    "[tauri] update_state: received {} setups; first tags: {} vs {}",
    newState.setups.len(),
    newState.setups.get(0).map(|s| s.p1.tag.as_str()).unwrap_or(""),
    newState.setups.get(0).map(|s| s.p2.tag.as_str()).unwrap_or(""),
  );

  for setup in &newState.setups {
    if setup.meta.best_of != 3 && setup.meta.best_of != 5 {
      return Err("bestOf must be 3 or 5 for all setups".into());
    }
  }
  *store.state.lock().unwrap() = newState.clone();
  write_state(&store.state_path, &newState)?;
  Ok(newState)
}

#[allow(non_snake_case)]
#[tauri::command]
fn swap_sides(store: TauriState<Store>, setupIndex: Option<usize>) -> Result<AllSetupsState, String> {
  let mut st = store.state.lock().unwrap();
  let idx = setupIndex.unwrap_or(0);

  if idx >= st.setups.len() {
    return Err(format!("setup_index {idx} out of range"));
  }

  let setup = &mut st.setups[idx];

  // Safe swap via clone to satisfy the borrow checker
  let tmp = setup.p1.clone();
  setup.p1 = setup.p2.clone();
  setup.p2 = tmp;

  // Normalize sides after swap
  setup.p1.side = "left".into();
  setup.p2.side = "right".into();

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
        state_path: state_path.clone(),
        state: Mutex::new(initial),
      });

      // Expose to Tauri commands
      app.manage(store.clone());

      // Start the embedded HTTP server for OBS
      let resources_dir = overlay_dir.join("resources");
      let upcoming_dir = overlay_dir.join("upcoming");
      let dual_dir = overlay_dir.join("dual");
      let quad_dir = overlay_dir.join("quad");

      // Ensure overlay subdirectories exist even if empty
      for dir in [&upcoming_dir, &dual_dir, &quad_dir] {
        fs::create_dir_all(dir).ok();
      }

      tokio::spawn(start_overlay_server(
        store.clone(),
        overlay_dir.clone(),
        resources_dir.clone(),
        "127.0.0.1:17890",
        "Main",
      ));

      tokio::spawn(start_overlay_server(
        store.clone(),
        upcoming_dir,
        resources_dir.clone(),
        "127.0.0.1:17891",
        "Upcoming",
      ));

      tokio::spawn(start_overlay_server(
        store.clone(),
        dual_dir,
        resources_dir.clone(),
        "127.0.0.1:17892",
        "Dual",
      ));

      tokio::spawn(start_overlay_server(
        store,
        quad_dir,
        resources_dir.clone(),
        "127.0.0.1:17893",
        "Quad",
      ));

      println!("Serving overlay dir: {}", overlay_dir.display());
      println!("State file: {}", state_path.display());

      Ok(())
    })
    .invoke_handler(tauri::generate_handler![get_state, update_state, swap_sides])
    .run(tauri::generate_context!())
    .expect("error while running tauri app");
}

fn overlay_router(store: Store, static_dir: PathBuf, resources_dir: PathBuf) -> Router {
  let static_files = get_service(ServeDir::new(static_dir));
  let resource_files = get_service(ServeDir::new(resources_dir));

  Router::new()
    .route(
      "/state.json",
      get({
        let store = store.clone();
        move || get_state_json(AxumState(store))
      }),
    )
    // Serve portraits and other shared assets from the main resources directory
    .nest_service("/resources", resource_files)
    .nest_service("/", static_files)
}

async fn start_overlay_server(
  store: Store,
  static_dir: PathBuf,
  resources_dir: PathBuf,
  addr: &str,
  label: &str,
) {
  let app = overlay_router(store, static_dir, resources_dir);

  let listener = TcpListener::bind(addr).await.unwrap_or_else(|e| panic!("bind {addr}: {e}"));
  println!("{label} overlay server at http://{addr}/ (open /index.html)");
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
