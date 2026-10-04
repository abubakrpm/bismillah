#!/usr/bin/env bash
# Builds both images, then compares size, user, and vulnerabilities.
# Requires: docker. Optional: trivy (https://trivy.dev)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Building naive image..."
docker build -f Dockerfile.naive -t demo-app:naive .

echo "==> Building optimized image..."
docker build -f Dockerfile -t demo-app:optimized .

echo
echo "==================== IMAGE SIZE ===================="
docker images demo-app --format "table {{.Tag}}\t{{.Size}}"

echo
echo "==================== RUNS AS ======================="
for tag in naive optimized; do
  user=$(docker run --rm --entrypoint whoami "demo-app:$tag")
  printf "%-10s %s\n" "$tag" "$user"
done

echo
echo "==================== LAYERS ========================"
for tag in naive optimized; do
  count=$(docker history -q "demo-app:$tag" | wc -l)
  printf "%-10s %s layers\n" "$tag" "$count"
done

if command -v trivy >/dev/null 2>&1; then
  echo
  echo "============ VULNERABILITIES (HIGH,CRITICAL) ======="
  for tag in naive optimized; do
    count=$(trivy image --quiet --severity HIGH,CRITICAL --format json "demo-app:$tag" \
      | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(len(r.get('Vulnerabilities') or []) for r in d.get('Results',[])))")
    printf "%-10s %s findings\n" "$tag" "$count"
  done
else
  echo
  echo "(Install trivy to also compare vulnerability counts)"
fi
