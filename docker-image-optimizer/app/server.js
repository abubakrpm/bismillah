const express = require("express");

const app = express();
const PORT = process.env.PORT || 3000;

app.get("/", (_req, res) => {
  res.json({ message: "Hello from an optimized container", version: "1.0.0" });
});

app.get("/health", (_req, res) => {
  res.status(200).json({ status: "ok" });
});

if (require.main === module) {
  app.listen(PORT, () => console.log(`Listening on port ${PORT}`));
}

module.exports = app;
