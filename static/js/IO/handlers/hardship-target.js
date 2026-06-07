import { registerHandler } from "../io-registry.js";

function render({ prompt, options, onSubmit }) {
  const wrap = document.createElement("div");
  wrap.innerHTML = `<p>${prompt}</p>`;

  options.forEach((player, index) => {
    const btn = document.createElement("button");
    btn.textContent = player.name;
    btn.onclick = () => onSubmit(index);
    wrap.appendChild(btn);
  });

  return wrap;
}

registerHandler("player_selector", render);