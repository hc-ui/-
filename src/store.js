export class NotesStore {
  constructor() {
    this.notes = [];
    this.nextId = 1;
  }

  list() {
    return [...this.notes];
  }

  create(title, body = "") {
    const trimmedTitle = String(title ?? "").trim();
    if (!trimmedTitle) {
      const error = new Error("Title is required");
      error.statusCode = 400;
      throw error;
    }

    const note = {
      id: this.nextId++,
      title: trimmedTitle,
      body: String(body ?? "").trim(),
      createdAt: new Date().toISOString(),
    };
    this.notes.unshift(note);
    return note;
  }

  delete(id) {
    const numericId = Number(id);
    const index = this.notes.findIndex((note) => note.id === numericId);
    if (index === -1) {
      return false;
    }
    this.notes.splice(index, 1);
    return true;
  }
}
