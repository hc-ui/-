# Notes starter

Small Node.js notes app for verifying the Cloud Agent development environment.

## Requirements

- Node.js 20 or newer

## Setup

```bash
npm ci
```

## Run

```bash
npm start
```

The server listens on `http://0.0.0.0:3000`.

- UI: `/`
- Health: `GET /api/health`
- Notes: `GET|POST /api/notes`, `DELETE /api/notes/:id`

## Test

```bash
npm test
```
