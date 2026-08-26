import assert from "node:assert/strict";
import { after, before, describe, it } from "node:test";
import { createApp } from "./app.js";
import { NotesStore } from "./store.js";

describe("notes API", () => {
  let server;
  let baseUrl;

  before(async () => {
    server = createApp(new NotesStore()).listen(0, "127.0.0.1");
    await new Promise((resolve) => server.once("listening", resolve));
    const { port } = server.address();
    baseUrl = `http://127.0.0.1:${port}`;
  });

  after(async () => {
    await new Promise((resolve, reject) => {
      server.close((error) => (error ? reject(error) : resolve()));
    });
  });

  it("reports health", async () => {
    const response = await fetch(`${baseUrl}/api/health`);
    const body = await response.json();
    assert.equal(response.status, 200);
    assert.equal(body.ok, true);
    assert.equal(body.service, "notes-starter");
  });

  it("creates, lists, and deletes a note", async () => {
    const created = await fetch(`${baseUrl}/api/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "环境检查", body: "从测试写入" }),
    });
    const createdBody = await created.json();
    assert.equal(created.status, 201);
    assert.equal(createdBody.note.title, "环境检查");

    const listed = await fetch(`${baseUrl}/api/notes`);
    const listedBody = await listed.json();
    assert.equal(listed.status, 200);
    assert.equal(listedBody.notes.length, 1);

    const deleted = await fetch(`${baseUrl}/api/notes/${createdBody.note.id}`, {
      method: "DELETE",
    });
    assert.equal(deleted.status, 204);

    const empty = await fetch(`${baseUrl}/api/notes`);
    const emptyBody = await empty.json();
    assert.equal(emptyBody.notes.length, 0);
  });

  it("rejects a note without a title", async () => {
    const response = await fetch(`${baseUrl}/api/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "  " }),
    });
    assert.equal(response.status, 400);
  });
});
