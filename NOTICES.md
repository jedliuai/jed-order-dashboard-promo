# 来源、第三方素材与依赖

## 产品画面

项目作者：**Jed杰德哥（jedliuai）**。产品入口：[个人订单驾驶舱](https://github.com/jedliuai/trade-order-dashboard-demo)；公网只读演示：[deskdemo.jedliuai.com](https://deskdemo.jedliuai.com/login)。宣传片 UI 素材采自该项目的虚构演示业务数据。截图保留 DEMO / 只读提示，不代表真实客户、实际收入或经营业绩。产品源代码属于独立仓库，不在本仓库重新授权。

## 鼠标点击与翻纸录音

两段原始录音来自 [Remotion Media](https://remotion.media/)。该站说明其音效可免版税使用且无需署名；这里仍保留来源，方便复核。

| 本仓库文件 | 来源 | 处理 |
| --- | --- | --- |
| `edit/presentation/public/assets/mouse-click-source.wav` | [mouse-click.wav](https://remotion.media/mouse-click.wav) | 原始录音 |
| `edit/presentation/public/assets/mouse-click-v2.wav` | 同上 | 裁切、整形后使用 |
| `edit/presentation/public/assets/paper-turn-source.wav` | [page-turn.wav](https://remotion.media/page-turn.wav) | 原始录音 |
| `edit/presentation/public/assets/paper-turns-v4.wav` | 同上 | 时间轴定位、音量处理并合成为总线 |

这些录音及其处理版本适用来源方的使用条件，不纳入作者原创素材授权。数据链音与配乐由仓库内 Python 合成程序生成。

## 软件、模型与字体

- [Remotion](https://www.remotion.dev/docs/license) 采用自身的 Free / Company License，请按团队规模和使用场景查看其现行条款。本仓库原创 JSX / TypeScript 的 MIT 授权不改变 Remotion 的许可。
- React、TypeScript、NumPy、SciPy、FFmpeg 等依赖保留自身许可；依赖通过包管理器安装，并未将全部依赖源码归为作者作品。
- 女声由本地 [CosyVoice](https://github.com/QwenAudio/CosyVoice) / CosyVoice2-0.5B 的通用“女主播”预设合成。模型权重、预设文件与本地运行环境不随仓库发布；安装和使用模型时应查看对应项目与权重的条款。
- 自动转写核验可使用 [SenseVoice](https://github.com/FunAudioLLM/SenseVoice)。自动识别仅作为辅助核验，不等同于人工听审。
- 字体使用系统 Microsoft YaHei、Segoe UI 等，仓库没有分发字体文件。其他系统字体替代可能改变中文排版。
- 封面通过 AI 图像生成工具按已确认文案和风格制作；提示词、比例记录与排版说明一并公开。封面中的小型界面图形经过生成模型重绘，不适合作为产品数值证明。Excel 等名称与标识仅用于说明业务场景，相关商标属于各自权利人。

媒体授权见 [MEDIA_LICENSE.md](MEDIA_LICENSE.md)，制作边界见 [docs/production.md](docs/production.md)。
