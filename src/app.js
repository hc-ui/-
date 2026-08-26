import express from "express";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { NotesStore } from "./store.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.join(__dirname, "..", "public");

export function createApp(store = new NotesStore()) {
  const app = express();
  app.use(express.json());
  app.use(express.static(publicDir));

  app.get("/api/health", (_req, res) => {
    res.json({
      ok: true,
      service: "notes-starter",
      time: new Date().toISOString(),
    });
  });

  app.get("/api/notes", (_req, res) => {
    res.json({ notes: store.list() });
  });

  app.post("/api/notes", (req, res) => {
    try {
      const note = store.create(req.body?.title, req.body?.body);
      res.status(201).json({ note });
    } catch (error) {
      res.status(error.statusCode ?? 500).json({ error: error.message });
    }
  });

  app.delete("/api/notes/:id", (req, res) => {
    const deleted = store.delete(req.params.id);
    if (!deleted) {
      res.status(404).json({ error: "Note not found" });
      return;
    }
    res.status(204).end();
  });

  return app;
}
