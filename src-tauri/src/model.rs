use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct PlayerState {
    pub side: String,            // "left" | "right"
    pub port: Option<u8>,        // 1..=4
    pub tag: String,
    pub sponsor: Option<String>,
    pub handle: Option<String>,  // @social
    pub character: String,       // e.g., "Mr. Game & Watch"
    pub character_color: String,         // e.g., "Blue"
    pub score: u32,
    pub country_code: Option<String>,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct CommentaryState {
    pub name: String,
    pub handle: Option<String>,
    pub active: Option<bool>,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct MatchMeta {
    pub tournament: Option<String>,
    pub round: String,
    pub best_of: u8,             // 3 or 5
    pub game_number: Option<u32>,
    pub stage: Option<String>,
    pub notes: Option<String>,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct OverlayState {
    pub p1: PlayerState,
    pub p2: PlayerState,
    pub meta: MatchMeta,
    pub commentators: Vec<CommentaryState>,
}
