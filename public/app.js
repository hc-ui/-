const healthEl = document.querySelector("#health");
const form = document.querySelector("#note-form");
const titleInput = document.querySelector("#title");
const bodyInput = document.querySelector("#body");
const notesEl = document.querySelector("#notes");

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (response.status === 204) {
    return null;
  }
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

async function refreshHealth() {
  try {
    const data = await fetchJson("/api/health");
    healthEl.textContent = `服务正常 · ${data.service}`;
    healthEl.className = "health ok";
  } catch {
    healthEl.textContent = "服务未就绪";
    healthEl.className = "health error";
  }
}

function renderNotes(notes) {
  notesEl.replaceChildren();
  if (!notes.length) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "还没有笔记。";
    notesEl.append(empty);
    return;
  }

  for (const note of notes) {
    const item = document.createElement("li");
    const heading = document.createElement("div");
    heading.className = "note-title";
    const title = document.createElement("strong");
    title.textContent = note.title;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "删除";
    remove.addEventListener("click", () => deleteNote(note.id));
    heading.append(title, remove);

    const body = document.createElement("p");
    body.textContent = note.body || "（无正文）";

    item.append(heading, body);
    notesEl.append(item);
  }
}

async function refreshNotes() {
  const data = await fetchJson("/api/notes");
  renderNotes(data.notes);
}

async function deleteNote(id) {
  await fetchJson(`/api/notes/${id}`, { method: "DELETE" });
  await refreshNotes();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await fetchJson("/api/notes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: titleInput.value,
      body: bodyInput.value,
    }),
  });
  form.reset();
  titleInput.focus();
  await refreshNotes();
});

await refreshHealth();
await refreshNotes();
