// types/overlay.ts

export type MeleeCharacter =
  | "Fox" | "Falco" | "Marth" | "Sheik" | "Jigglypuff" | "Captain Falcon" | "Peach"
  | "Ice Climbers" | "Pikachu" | "Yoshi" | "Samus" | "Dr. Mario" | "Luigi" | "Mario"
  | "Young Link" | "Ganondorf" | "Donkey Kong" | "Link" | "Ness" | "Mewtwo"
  | "Mr. Game & Watch" | "Roy" | "Pichu" | "Zelda" | "Bowser" | "Kirby";

export type CharacterColor =
  | "Default" | "Red" | "Blue" | "Green" | "Black" | "White" | "Yellow"
  | "Pink" | "Purple" | "Orange" | "Teal" | string;

export type Port = 1 | 2 | 3 | 4;
export type Side = "left" | "right";
export type RoundCode = "R1" | "R2" | "R3" | "QF" | "SF" | "WF" | "LF" | "GF" | string;
export type BestOf = 3 | 5;

export interface PlayerState {
  side: Side;
  port?: Port;
  tag: string;
  sponsor?: string;
  handle?: string;            
  character: MeleeCharacter;
  characterColor: CharacterColor;
  score: number;
  country_code?: string;      
}

export interface CommentaryState {
  name: string;
  handle?: string;            
  active?: boolean;
}

export interface MatchMeta {
  tournament?: string;
  round: RoundCode;
  bestOf: BestOf;             
  gameNumber?: number;
  stage?: string;
  notes?: string;
}

export interface OverlayState {
  p1: PlayerState;
  p2: PlayerState;
  meta: MatchMeta;
  commentators: CommentaryState[];
}