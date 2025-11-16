import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { OverlayState } from "../types/overlay";
import "./App.css";
import {
  CHARACTER_COLORS,
  ALL_CHARACTERS,
  type CharacterName,
} from "./characters";



export default function App() {
  const [state, setState] = useState<OverlayState | null>(null);

  useEffect(() => {
    invoke<OverlayState>("get_state").then(setState).catch(console.error);
  }, []);

  async function save() {
    if (!state) return;
    await invoke("update_state", { newState: state });
  }

  async function swap() {
    const updated = await invoke<OverlayState>("swap_sides");
    setState(updated);
  }

  const updateField = (path: string, value: string | number) => {
    setState((prev) => {
      if (!prev) return prev;
      const clone: any = structuredClone(prev);
      const keys = path.split(".");
      let obj = clone;
      while (keys.length > 1) obj = obj[keys.shift()!];
      obj[keys[0]] = value;
      return clone;
    });
  };

  const onCharacterChange = (playerKey: "p1" | "p2", newChar: CharacterName) => {
    const colors = CHARACTER_COLORS[newChar] ?? [];
    const newColor = (colors.includes("Default") ? "Default" : colors[0]) ?? "";
    setState((prev) => {
      if (!prev) return prev;
      const clone: any = structuredClone(prev);
      clone[playerKey].character = newChar;
      clone[playerKey].characterColor = newColor;
      return clone;
    });
  };

  const colorsFor = (charName?: string) =>
    (charName ? CHARACTER_COLORS[charName as CharacterName] : undefined) ?? [];

  if (!state) return <p className="loading">Loading current match…</p>;

  const { p1, p2, meta } = state;

  return (
    <main className="app">

      {/* === MATCH META === */}
      <section>
        <div className="meta">
          <input
            value={meta.round}
            onChange={(e) => updateField("meta.round", e.target.value)}
            placeholder="Title"
          />
          <select
            value={meta.bestOf}
            onChange={(e) =>
              updateField("meta.bestOf", Number(e.target.value))
            }
          >
            <option value={3}>Best of 3</option>
            <option value={5}>Best of 5</option>
          </select>


        </div>
      </section>
      {/* === PLAYERS === */}
      <section>
        <div className="players">
          {/* === P1 === */}
          <div className="player">
            <input
              value={p1.tag}
              onChange={(e) => updateField("p1.tag", e.target.value)}
              placeholder="Tag"
            />
            {/* <input
              value={p1.handle ?? ""}
              onChange={(e) => updateField("p1.handle", e.target.value)}
              placeholder="@handle"
            /> */}

            {/* Character select */}
            <select
              value={(p1.character as CharacterName | undefined) ?? ""}
              onChange={(e) =>
                onCharacterChange("p1", e.target.value as CharacterName)
              }
            >
              <option value="" disabled>
                Choose character…
              </option>
              {ALL_CHARACTERS.map((c: CharacterName) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>

            {/* Color select */}
            <select
              value={p1.characterColor ?? ""}
              onChange={(e) => updateField("p1.characterColor", e.target.value)}
              disabled={!p1.character}
            >
              <option value="" disabled>
                {p1.character ? "Choose color…" : "Select a character first"}
              </option>
              {colorsFor(p1.character).map((col: string) => (
                <option key={col} value={col}>
                  {col}
                </option>
              ))}
            </select>

            <input
              type="number"
              value={p1.score}
              onChange={(e) => updateField("p1.score", Number(e.target.value))}
            />
          </div>

          {/* === P2 === */}
          <div className="player">
            <input
              value={p2.tag}
              onChange={(e) => updateField("p2.tag", e.target.value)}
              placeholder="Tag"
            />
            {/* <input
              value={p2.handle ?? ""}
              onChange={(e) => updateField("p2.handle", e.target.value)}
              placeholder="@handle"
            /> */}

            <select
              value={(p2.character as CharacterName | undefined) ?? ""}
              onChange={(e) =>
                onCharacterChange("p2", e.target.value as CharacterName)
              }
            >
              <option value="" disabled>
                Choose character…
              </option>
              {ALL_CHARACTERS.map((c: CharacterName) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>

            <select
              value={p2.characterColor ?? ""}
              onChange={(e) => updateField("p2.characterColor", e.target.value)}
              disabled={!p2.character}
            >
              <option value="" disabled>
                {p2.character ? "Choose color…" : "Select a character first"}
              </option>
              {colorsFor(p2.character).map((col: string) => (
                <option key={col} value={col}>
                  {col}
                </option>
              ))}
            </select>

            <input
              type="number"
              value={p2.score}
              onChange={(e) => updateField("p2.score", Number(e.target.value))}
            />
          </div>
        </div>

        <div className="buttons">
          <button onClick={swap}>Swap Sides</button>
          <button onClick={save}>Save State</button>
        </div>
      </section>
    </main>
  );
}
