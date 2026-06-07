import { registerHandler } from "../io-registry.js";

registerHandler("card-grid", ({ cards, prompt, onSubmit }) => {
  const div = document.createElement("div");
  div.className = "io-card-grid";

  (cards ?? []).forEach((card, i) => {
    const btn = document.createElement("button");
    btn.textContent = card.name ?? `Carte ${i}`;
    btn.onclick = () => onSubmit(i);
    div.appendChild(btn);
  });

  return div;
});