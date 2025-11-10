// Exact folder/file names from resources/characters/vs_screen/<Character>/<Color> <Side>.png

// Define the canonical character name union for strong typing.
// If you add/remove a character, update this type and the map below.
export type CharacterName =
  | "Bowser"
  | "Captain Falcon"
  | "Donkey Kong"
  | "Dr Mario"
  | "Falco"
  | "Fox"
  | "Ganondorf"
  | "Ice Climbers"
  | "Jigglypuff"
  | "Kirby"
  | "Link"
  | "Luigi"
  | "Mario"
  | "Marth"
  | "Mewtwo"
  | "Mr Game & Watch"
  | "Ness"
  | "Peach"
  | "Pichu"
  | "Pikachu"
  | "Roy"
  | "Samus"
  | "Sheik"
  | "Yoshi"
  | "Young Link"
  | "Zelda";

export const CHARACTER_COLORS = {
  Bowser: ["Default", "Red", "Blue", "Black"],
  "Captain Falcon": ["Default", "Red", "Blue", "Green", "White", "Black"],
  "Donkey Kong": ["Default", "Red", "Blue", "Green", "Purple"],
  "Dr Mario": ["Default", "Red", "Blue", "Green", "Black"],
  Falco: ["Default", "Red", "Blue", "Green"],
  Fox: ["Default", "Red", "Blue", "Green"],
  Ganondorf: ["Default", "Red", "Blue", "Green", "Purple"],
  "Ice Climbers": ["Default", "Red", "Green", "Orange"],
  Jigglypuff: ["Default", "Red", "Blue", "Green", "Yellow"],
  Kirby: ["Default", "Red", "Blue", "Green", "White", "Yellow"],
  Link: ["Default", "Red", "Blue", "White", "Black"],
  Luigi: ["Default", "Blue", "Pink", "White"],
  Mario: ["Default", "Blue", "Brown", "Green", "Yellow"],
  Marth: ["Default", "Red", "Blue", "Green", "White", "Black"],
  Mewtwo: ["Default", "Blue", "Green", "Yellow"],
  "Mr Game & Watch": ["Default", "Red", "Blue", "Green"],
  Ness: ["Default", "Blue", "Green", "Yellow"],
  Peach: ["Default", "Blue", "Green", "White", "Yellow"],
  Pichu: ["Default", "Red", "Blue", "Green"],
  Pikachu: ["Default", "Red", "Blue", "Green"],
  Roy: ["Default", "Red", "Blue", "Green", "Yellow"],
  Samus: ["Default", "Brown", "Green", "Pink", "Purple"],
  Sheik: ["Default", "Red", "Blue", "Green", "Purple"], // separate folder
  Yoshi: ["Default", "Red", "Blue", "Cyan", "Pink", "Yellow"],
  "Young Link": ["Default", "Red", "Blue", "White", "Black"],
  Zelda: ["Default", "Red", "Blue", "Green", "Purple"], // Sheik removed
} as const satisfies Record<CharacterName, readonly string[]>;

export const ALL_CHARACTERS = Object.keys(CHARACTER_COLORS) as CharacterName[];
