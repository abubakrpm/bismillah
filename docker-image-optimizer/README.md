# Docker Image Optimizer

A small Node.js (Express) API packaged two ways, so you can measure the difference between a naive Dockerfile and an optimized one.

| | `Dockerfile.naive` | `Dockerfile` (optimized) |
|---|---|---|
| Base image | `node:22` (full Debian) | `node:22-alpine` |
| Build strategy | Single stage | Multi-stage (build → deps → runtime) |
| Dev dependencies in image | Yes | No |
| Tests run during build | No | Yes, build fails if tests fail |
| Layer caching | Broken by any code change | Deps cached until `package.json` changes |
| User | root | `node` (non-root) |
| Healthcheck | No | Yes |
| PID 1 | `npm` | `node` (receives SIGTERM properly) |

## Project structure

```
docker-image-optimizer/
├── app/
│   ├── server.js          # Express API: / and /health
│   ├── server.test.js     # Tests (node:test + supertest)
│   └── package.json
├── Dockerfile             # Optimized multi-stage build
├── Dockerfile.naive       # The "before" version
├── .dockerignore
└── scripts/compare.sh     # Builds both and prints a comparison
```

## Run it

```bash
# Compare both images (size, user, layers, and CVEs if trivy is installed)
chmod +x scripts/compare.sh
./scripts/compare.sh

# Run the optimized container
docker run -d -p 3000:3000 --name demo demo-app:optimized
curl localhost:3000/health
docker inspect --format '{{.State.Health.Status}}' demo
```

Run the app without Docker:

```bash
cd app && npm install && npm test && npm start
```

## Things to try

1. Change a line in `server.js` and rebuild both images. Watch which one reuses the `npm install` layer.
2. Make a test fail on purpose. The optimized build stops; the naive one ships it anyway.
3. Run `docker run --rm demo-app:naive whoami` vs `demo-app:optimized`.
4. Scan both: `trivy image demo-app:naive` vs `trivy image demo-app:optimized`.

## Results

Record your own numbers here after running `compare.sh`:

| Metric | Naive | Optimized |
|---|---|---|
| Image size | | |
| HIGH/CRITICAL CVEs | | |
| Rebuild time after code change | | |
