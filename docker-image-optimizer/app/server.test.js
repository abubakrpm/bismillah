const { test } = require("node:test");
const assert = require("node:assert");
const request = require("supertest");
const app = require("./server");

test("GET / returns a message", async () => {
  const res = await request(app).get("/");
  assert.strictEqual(res.status, 200);
  assert.ok(res.body.message);
});

test("GET /health returns ok", async () => {
  const res = await request(app).get("/health");
  assert.strictEqual(res.status, 200);
  assert.strictEqual(res.body.status, "ok");
});
