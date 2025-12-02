# gr-sdrv1

GNU Radio 3.10 的 Out-Of-Tree 模块（OOT），为 SDRV1 射频硬件提供基于 libiio 的收发数据流接口，并带有 GRC 图形块。

本仓库包含：
- C++ 实现的发送块：`sdrv1stream_sink`（支持 GRC）
- Python 实现的发送块：`sdrv1_sink`
- Python 实现的接收块：`sdrv1_source_fc32`
- 对应的 GRC 块描述：`grc/sdrv1_*.block.yml`

硬件通过 IIO 网络上下文连接（例如 192.168.x.x），内部设备名称默认：
- 物理设备：`nrf9022-phy`
- TX 流：`avc_txstream`
- RX 流：`avc_rxstream`


## 功能与块概览

- sdrv1_source_fc32（Python）：
	- 输出类型：complex float32
	- 关键参数：ip（板卡 IP）、channel（rx1/rx2）、buf_len、gain、fs、bw、lo
	- 运行时方法：`set_rx_gain(fs/bw/lo)`，在大幅变化时自动触发 DCOC

- sdrv1_sink（Python）：
	- 输入类型：complex float32
	- 关键参数：ip、channel（tx1/tx2）、buf_len、gain、fs、bw、lo
	- 运行时方法：`set_tx_gain(fs/bw/lo)`，在大幅变频时自动执行 TX 校准

- sdrv1stream_sink（C++）：
	- 输入类型：complex（gr_complex）
	- 关键参数：ip、chn（tx1/tx2）、buffer_size
	- 通过 libiio 直接写入 `avc_txstream` 设备缓冲


## 软件依赖

编译时：
- GNU Radio 3.10（开发头文件与 cmake 模块）
- CMake ≥ 3.8（推荐 3.14+）
- C/C++ 编译器（支持 C++11/14）
- libiio（含头文件与库）
- 可选：Doxygen（生成文档）

运行时：
- GNU Radio 运行环境（含 GRC）
- pylibiio（Python 的 `iio` 模块）

可选/推荐：使用 conda（conda-forge）统一安装 gnuradio、libiio、pylibiio。

仓库附带的一键脚本：
- Linux/macOS 类似环境：`install.sh`（示例基于 Linux，创建 `gnuradio` conda 环境并安装 gnuradio 与 gnuradio-iio）
- Windows：`install.bat`（Miniconda + `gnuradio` 环境）

提示：顶层 `CMakeLists.txt` 中存在面向 Windows Miniforge 的默认路径（如 CMAKE_INSTALL_PREFIX、GR_PYTHON_DIR 等）；在本机构建时请通过命令行选项覆盖这些变量。


## 编译与安装

下面给出三种常见方式。任选其一。

### 方式 A：conda 环境（跨平台推荐）
1) 准备环境（示例）：
	 - 创建并激活环境：`conda create -n gnuradio -c conda-forge gnuradio libiio pylibiio cmake ninja make -y`，`conda activate gnuradio`
2) 配置与编译安装：
	 - 构建目录：`mkdir build && cd build`
	 - 运行 CMake（关键是指向 conda 前缀，并设置 Python 包输出目录）：
		 - `-DCMAKE_PREFIX_PATH="$CONDA_PREFIX"`
		 - `-DGR_PYTHON_DIR="$(python -c 'import site; print(site.getsitepackages()[0])')"`
		 - 可选：`-DENABLE_TESTING=OFF`
	 - 构建并安装：`cmake --build . -j`，`cmake --install .`

示例（macOS/Linux，zsh/bash）：
```
mkdir -p build && cd build
cmake -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" \
			-DGR_PYTHON_DIR="$(python -c 'import site; print(site.getsitepackages()[0])')" \
			-DENABLE_TESTING=OFF ..
cmake --build . -j
cmake --install .
```

### 方式 B：系统包管理器（Ubuntu/Debian）
```
sudo apt update
sudo apt install -y gnuradio-dev libiio-dev cmake g++
mkdir -p build && cd build
cmake -DENABLE_TESTING=OFF ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

如需指定 Python 安装目录，可在 cmake 命令中附加：
`-DGR_PYTHON_DIR=$(python3 -c 'import site; print(site.getsitepackages()[0])')`

### 方式 C：macOS（Homebrew）
```
brew install gnuradio libiio cmake
mkdir -p build && cd build
cmake -DCMAKE_PREFIX_PATH="$(brew --prefix)/opt/gnuradio;$(brew --prefix)/opt/libiio" \
			-DGR_PYTHON_DIR="$(python3 -c 'import site; print(site.getsitepackages()[0])')" \
			-DENABLE_TESTING=OFF ..
cmake --build . -j
sudo cmake --install .
```

安装完成后，GRC 应在分类 `[sdrv1]` 下显示新增块；若未显示，请检查 `PYTHONPATH` 与 `GRC_BLOCKS_PATH` 是否包含安装目录。


## 快速上手（GRC）

发送：
- 典型链路：`Signal Source/Vector Source` → `Throttle` → `sdrv1_sink`
- 关键参数：
	- ip：目标板 IP（例：`192.168.2.10`）
	- channel：`tx1` 或 `tx2`
	- buf_len：如 `8192`
	- fs/bw/lo/gain：示例 `fs=2e6, bw=2e6, lo=110e6, gain=16`
- 注意：输入复数幅度建议 |x| ≤ 1，否则会触发幅度检查异常。

接收：
- 典型链路：`sdrv1_source` → `QT GUI Time/Freq Sink` 或文件保存
- 关键参数：
	- channel：`rx1` 或 `rx2`
	- 其他同上；改变 LO 时，模块会按需进行 DCOC。

块参数范围（来自 GRC 断言）：
- fs < 40e6，bw < 40e6
- 50 MHz ≤ lo ≤ 5 GHz
- RX 增益：[-2, 77] dB；TX 增益：[0, 43] dB


## 文档与测试

- 若安装了 Doxygen，可生成 API 文档（若 CMake 启用了 docs 子目录）：
	- `cmake --build . --target docs`（目标名称因环境可能不同）
- 单元测试示例位于 `python/sdrv1/qa_*.py`；其中部分测试依赖真实硬件与 IP 地址。


## LICENSE 说明

本项目已统一为 GPL-3.0-or-later，并在源码文件头部以 SPDX 标识声明。根目录 `LICENSE` 已提供对应的许可文本；conda-forge 配方已设置 `license: GPL-3.0-or-later` 与 `license_file: LICENSE`。


## 兼容性与常见问题

- CMake 默认 Windows Miniforge 路径：请在本机构建时用 `-DCMAKE_PREFIX_PATH`、`-DCMAKE_INSTALL_PREFIX`、`-DGR_PYTHON_DIR` 覆盖。
- 找不到 `iio` 模块：请安装 `pylibiio`（conda-forge 包名为 `pylibiio`，有时也随 `libiio` 安装 Python 绑定）。
- GRC 中看不到模块：确认 Python 与 GRC 的搜索路径指向了本项目安装位置。
- 运行时报硬件设备名不存在：确认目标板连通且设备名与本模块默认配置匹配（`nrf9022-phy`、`avc_txstream`、`avc_rxstream`）。


## 贡献

欢迎以 PR/Issue 的形式反馈问题与改进建议。
