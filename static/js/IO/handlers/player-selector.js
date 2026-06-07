import { registerHandler } from "../io-registry.js";

registerHandler("player-selector", ({ players, prompt, onSubmit }) => {
  const div = document.createElement("div");
  div.className = "io-player-selector";

  (players ?? []).forEach((name, i) => {
    const btn = document.createElement("button");
    btn.textContent = name;
    btn.onclick = () => onSubmit(i);
    div.appendChild(btn);
  });

  return div;
});