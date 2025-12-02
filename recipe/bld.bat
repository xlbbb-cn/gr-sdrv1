@echo on
setlocal enabledelayedexpansion

mkdir build
cd build

for /f "usebackq delims=" %%i in (`"%PYTHON%" -c "import site; print(site.getsitepackages()[0])"`) do set PY_SITE=%%i

cmake -G "Ninja" ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DCMAKE_PREFIX_PATH="%PREFIX%" ^
  -DCMAKE_INSTALL_PREFIX="%PREFIX%" ^
  -DGR_PYTHON_DIR="%PY_SITE%" ^
  -DENABLE_TESTING=OFF ^
  ..

cmake --build . --parallel %CPU_COUNT%
cmake --install .

endlocal