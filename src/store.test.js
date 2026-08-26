import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { NotesStore } from "./store.js";

describe("NotesStore", () => {
  it("creates and lists notes newest first", () => {
    const store = new NotesStore();
    const first = store.create("First", "alpha");
    const second = store.create("Second", "beta");

    assert.equal(first.id, 1);
    assert.equal(second.id, 2);
    assert.deepEqual(
      store.list().map((note) => note.title),
      ["Second", "First"],
    );
  });

  it("rejects a blank title", () => {
    const store = new NotesStore();
    assert.throws(() => store.create("   "), { statusCode: 400 });
    assert.equal(store.list().length, 0);
  });

  it("deletes an existing note and ignores missing ids", () => {
    const store = new NotesStore();
    const note = store.create("Keep me");
    assert.equal(store.delete(note.id), true);
    assert.equal(store.delete(note.id), false);
    assert.equal(store.list().length, 0);
  });
});
