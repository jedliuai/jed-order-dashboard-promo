# 音乐、旁白与混音复现

发布成片为 `deliverables/promo-60s-music-only.mp4` 和 `deliverables/promo-60s-narrated.mp4`，两者都是 1920×1080、30 fps、1800 帧、60 秒。女声讲解版直接复制音乐版的视频码流，仅替换声音。单独旁白是 `deliverables/narration.wav`，已混合的人声加音乐为 `deliverables/soundtrack-narrated.wav`。

基础复现无需模型或 GPU：仓库已保存最终逐段讲解 WAV 和全部音乐、翻纸、节点音、鼠标点击。使用 Python 3.10 或更新版本、`requirements.txt` 中的 NumPy/SciPy/Pillow，以及可从命令行调用的 FFmpeg、FFprobe。模型生成和离线识别是可选流程，不在基础依赖中安装 PyTorch、CosyVoice 或 FunASR。

```bash
python -m pip install -r requirements.txt
ffmpeg -version
ffprobe -version
```

## 用保存素材重做讲解版

正文和预留声窗来自 `edit/narration/voice-jobs.json`，最终原始片段在 `edit/narration/voice-clips/`。混音脚本先检测片段有效声音，保留轻辅音和词尾，必要时进行不超过 1.19 倍的保调速率微调；使用 70 Hz 高通、轻度压缩和双遍响度处理，再按固定时间放入 60 秒旁白。

推荐先写 `output/` 中的副本，保持发布文件原样：

```bash
python edit/narration/mix_narration.py --output-dir output/reproduction --target output/reproduction/promo-60s-narrated.mp4 --narration-output output/reproduction/narration.wav
python edit/narration/verify_narrated_video.py --target output/reproduction/promo-60s-narrated.mp4 --narration output/reproduction/narration.wav --mix-report output/reproduction/mix-report.json --output-dir output/reproduction
```

不传输出参数时，混音脚本会更新规范命名的讲解成片和旁白文件。`--output-dir` 控制中间 WAV、对齐片段与报告；`--target` 和 `--narration-output` 控制两个最终输出。无口播音乐版始终作为输入，不会被覆盖。`output/` 全目录应保持 Git 忽略。

验收脚本检查原音乐版 SHA-256、两个版本的视频包 SHA-256 完全一致、1080p/30 fps/1800 帧/60 秒、完整解码无错误、实际 AAC 音轨响度和真峰、两次点击各 150 毫秒的无旁白留白，以及最后一句及时收尾。它只依赖当前发布文件，不需要历史版本。默认原音乐版 SHA-256 为 `BE226EDDCDB0A6C90CDA41921BB9FA60C06A8B146FFCC98D4138B3860C7EB6C4`；若有意重新渲染音乐版，先确认新的输入，再通过两个脚本的 `--expected-source-sha256` 显式指定新哈希。

检查已保存的发布成片时，可以直接运行：

```bash
python edit/narration/verify_narrated_video.py
```

默认优先读取 `output/narration/mix-report.json`，不存在时尝试 `edit/narration/mix-report.json`。这份对齐报告是可选的；没有报告也能从最终 `narration.wav` 检查点击留白和实际词尾时间，不会要求补齐历史资料。新报告和解码检查 WAV 写入忽略的 `output/narration/`。报告只包含时间、数值、素材标识和哈希，不记录本机绝对路径。

混音保留原音乐 0.92 的曲线：节点处降低到 0.66、点击处降低到 0.65。说话时仅音乐再乘 0.36，提前 150 毫秒压低、300 毫秒恢复；小于 0.65 秒的短停顿维持低档。翻纸 0.68、八颗递升节点音 0.93、点击 0.90 保持原卡点。旁白处理目标是单声道 -19 LUFS，复制到立体声混合总线后相当于约 -16 LUFS；整片总线按约 -16 LUFS 调整，保留递进编曲。

原成片与重新混音的 AAC 封装哈希可能随 FFmpeg、编码器和平台版本变化。验收重点是视频包不变、时间和技术指标通过；这不等同于所有环境都能得到同一个 MP4 文件哈希。发布成片保持原交付字节，不用测试副本覆盖它。

本次公开目录复现实测使用 Python 3.13.6、NumPy 2.2.1、SciPy 1.17.0、FFmpeg 8.1。15 段保存素材重新对齐、混音后的 MP4、单独旁白 WAV 和完整混合 WAV，分别与三个原交付文件的 SHA-256 完全一致；原交付文件未被覆盖。实际 AAC 为 -16.01 LUFS、-4.48 dBTP，1800 帧/60 秒，完整解码无错误，两次点击各 150 毫秒无旁白。详见 [发布文件验收](verification/narration-verification.json) 和 [保存素材复现](verification/narration-reproduction.json)。可选 TTS/ASR 本轮未执行模型推理。

## 原创电子配乐与卡点音

`edit/audio/generate_score_v4.py` 只依赖同目录 `synth_instruments.py`、统一时间表 `edit/presentation/src/timeline-v4.json` 和真实翻纸源 `edit/presentation/public/assets/paper-turn-source.wav`。不依赖旧版生成脚本或旧版音乐。鼠标点击保留最终资产名 `mouse-click-v2.wav`，由影片或混音脚本在第 618、1463 帧放入，没有混进纸声或节点轨。

音乐采用本地合成，固定随机种子：前 7 秒简洁和弦与拨弦，鼓和贝斯逐层渐入，19 秒节奏成型，34.5 秒加入更密的打击、切分与高音旋律，51–56.5 秒进入高潮，最后 3.5 秒收束。八颗短尾玻璃/木琴式敲击仅在第 225、240、255、270、285、300、315、330 帧出现，MIDI 为 72、74、76、79、81、84、86、88；逐颗以主 RMS 能量峰对齐点亮帧。其他转场只用一层真实翻纸。

无需重新生成即可混音。若想实验配乐但保留现有音轨，可把三条新 WAV 和报告都放入忽略目录：

```bash
python edit/audio/generate_score_v4.py --assets-dir output/audio/assets --output-dir output/audio
```

不传 `--assets-dir` 时，脚本会更新 `edit/presentation/public/assets/` 下的 `music-v4.wav`、`paper-turns-v4.wav`、`flow-chimes-v4.wav`；它不会生成鼠标点击。报告与自动说明默认写入 `output/audio/`。`--timeline` 和 `--paper-source` 可替换对应输入，默认读取仓库保存素材。每条最终音轨是 48 kHz、立体声、60 秒，每声道 2,880,000 采样；每个视频帧对应 1,600 采样。

## 可选：用自己的本地模型重新配音

重新生成 TTS 需要自行准备兼容的本地 CosyVoice2 环境、`pretrained_models/CosyVoice2-0.5B/` 和 `voices/<音色名>.pt`。原声线参考文件与模型权重没有随仓库发布；已保存的最终讲解片段足以完成基础复现。声线文件须包含当前接口需要的 `text_ref` 与 `audio_ref`。这个适配脚本采用 CUDA 和半精度推理，请使用模型工程匹配的 PyTorch/CUDA 环境，不要只靠基础 `requirements.txt` 安装模型。

本机路径通过 `--model-root` 或 `COSYVOICE_ROOT` 环境变量提供，没有固定磁盘或用户名。用模型环境的 Python 执行以下命令，将 `<local-cosyvoice-root>` 替换为自己的本地目录：

```bash
python edit/narration/generate_local_voice.py --model-root "<local-cosyvoice-root>" --jobs edit/narration/voice-jobs.json --output-dir output/narration/segments --voice "女主播"
```

脚本在进入模型目录前解析 jobs 与输出目录，开启离线环境标志，不下载模型或改写参考声线。缓存核对正文、音色、速度和随机种子；改变内容会重新生成，`regenerate` 可强制刷新。生成报告只保存片段文件名、Python 版本、模型/设备标识、时间和哈希，不写可执行文件绝对路径。TTS 在不同 GPU、模型版本或依赖版本下仍可能生成不同波形；重新生成原音色需要自行提供兼容声线。

## 可选：离线识别回查

同一模型根目录下需要已经存在 `SenseVoiceSmall/` 和安装好的 FunASR。下例使用 CPU；设备可改成兼容环境中的 `cuda:0`：

```bash
python edit/narration/check_local_speech.py --model-root "<local-cosyvoice-root>" --input-dir output/reproduction --glob "*-aligned.wav" --report output/reproduction/asr-aligned.json --device cpu
```

ASR 报告只记录片段文件名与识别文字。同音、近音词转写并不等于画面文字或人工听审结论；自然度、辅音完整性和卡点提示是否清楚，仍需要实际播放检查。公开移植的基础混音已用保存素材验证；可选 TTS/ASR 入口只做参数与路径检查，不作为未经重新推理的模型跨环境保证。
