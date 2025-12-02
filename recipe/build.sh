#!/usr/bin/env bash
set -exuo pipefail

# Configure build dir
mkdir -p build
cd build

# Compute Python site-packages under PREFIX
PYTHON_SITE=$($PYTHON - <<'PY'
import site
print(site.getsitepackages()[0])
PY
)

cmake -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="${PREFIX}" \
  -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
  -DGR_PYTHON_DIR="${PYTHON_SITE}" \
  -DENABLE_TESTING=OFF \
  ..

cmake --build . --parallel ${CPU_COUNT:-1}
cmake --install .
