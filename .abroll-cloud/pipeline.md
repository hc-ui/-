# A-roll / B-roll 云端流水线简报

给兄弟智能体用。这是**普通短视频 / 知识口播**管线，**不是**剧情短剧，**不要**执行或发明 `drama-pipeline`。

Drive 笔记只读。本机 Windows / `C:\` / `D:\` / `G:\` / `C:\Obsidian Valut\...` **禁止访问、禁止写入**。全部工作只在 `/workspace`。

---

## 0. 云端红线

- 工作根：`/workspace/.abroll-cloud/`
- 单集：`/workspace/.abroll-cloud/<NN>_<中文名>/`（已有空壳可用 `01/`）
- 中间文件：同集目录或 `/workspace/.abroll-cloud/_scratch/`
- **禁止**把草稿、静帧、临时 json、半成品、未完成渲染放进 `/workspace/成片/`
- 成品文件名：`00_最终成片_<名>.mp4`、`00_封面_<名>.jpg`，先放在**该集项目根**
- `/workspace/成片/` 若被投递约定当作中转，只允许**已稳定成片**的拷贝，不是渲染目录；本简报不写 Drive
- 当前选题见同目录 `topics.md`（知识口播，不是短剧）
- Google Drive MCP：只 `search_files` / `read_file_content` / `get_file_metadata`，禁止 create / update / trash / share / copy
- 缺 TTS / Whisper / FFmpeg / 生图时：交出原文、时间轴、画面任务和本集绝对路径，**不得假装已生成**
- 禁止多路并行狂渲
- 凭据只读环境变量名，不写 key

---

## 1. 先分型（来自《AI视频创作技能地图》）

| 类型 | 识别 | 本云端任务 |
|------|------|------------|
| 普通短视频 | 观点、知识、教程、口播、信息图；画面解释节奏，不靠角色演完情节 | **走本简报** |
| 剧情短剧 | 人物、冲突、选择、跨镜连续性决定成败 | **不做**。不要套五层短剧，不要写资产圣经/分镜帧流水 |

用户已指定知识 / 口播 / A-B-roll → 直接本管线。混合项目看「哪一块决定成败」：信息表达走这里。

---

## 2. 知识视频三步（来自《知识视频三步实操》）

口播知识片的最小方法，不要先堆素材：

1. **先写整段口播**（一口气可读完；图跟着声音走，不是声音跟着图走）
2. **按短语切开**（每段 5–15 字；**一段只给一个画面任务**，不要一段塞三件事）
3. **两种镜头轮着切**
   - **A 卷 / A-roll**：白底小剧场，软 3D 搪胶 IP「小灯」负责说话（`assets/V-*.mp4`）
   - **B 卷 / B-roll**：黑底信息图负责讲清楚（`broll/B-*.mp4`，代码绘制，**生图不烧中文**）

---

## 3. 标准生产顺序（来自《AI短视频制作工作流》）

方向未定时只交最小文案/视觉方案，等人选定。方向和文案已明确、要求连续做完时，**不要**按短剧五层逐层停顿。

1. **定义成片目标**：受众、竖屏 9:16、目标时长、核心表达、一句话钩子。
2. **锁定整段文案**：钩子 → 单一主线 → 回报/余韵。**先给场景，再给方法**。写成 `script/voiceover.txt`。只要方向时不要提前扩生产包。开场常用「大家好。」
3. **整段配音 + 短语对齐**：整条旁白一次合成。输出 `audio/vo-full.wav`（44100 Hz、单声道或立体声均可，成片混音到 44100 AAC）。对齐到 `script/phrases.txt` / `audio/vo-align.txt`。识别文字**只取时间戳**，正文永远以原文为准。时间轴**无重叠、无空缺**，末段结束时间 = 音频总时长。
4. **按短语设计画面**：每段在 A-roll / B-roll / 信息图 / 字幕里选一种。重复角色才锁资产，**不强制**完整资产表和分镜帧。
5. **生产素材与动效**：A 卷用已有小灯动作或本机会话真实具备的视频工具；B 卷用代码/PIL/FFmpeg 画黑底卡。中文标题和字幕**全部组装阶段叠加**。
6. **按旁白时间轴组装**：画面跟随已锁定旁白，不让素材时长反过来改文案。控制切镜密度，**避免每个短语都机械切一次**。
7. **核验并交付**：写 `项目说明.md` + `项目状态.json`；核验分辨率、帧率、时长、音轨、时间轴闭合。最终回复先给成片路径和剩余风险。

---

## 4. 画面语言与切镜铁律

- 风格：白底小灯 A + 黑底信息图 B。A 在白棚；B 无角色生图。
- **B 卷要比口播早切半拍**：话音未落，图先到位；听众先看见，再听见解释。
- **不要白闪**：A↔B 用色块快门。常见色：A 侧奶油 `[245,247,250]`，B 侧薄荷 `[126,224,197]`。
- A 卷可 `close: true` 再近一点（组装脚本会放大裁切）。
- B 卷对照卡只打一个点，左右反差，不要目录墙。
- 垫乐盖不住口播：BGM 约 `volume=0.18`，可 `adelay=800ms`，口播 loudnorm 约 `I=-16`。
- 切镜音效可叠，音量约 `0.30`，不要抢词。
- 不要 6 秒同机位死画面；长句拆拍点，不要靠空镜拖。

### 口播写作禁忌（同管线已落地的集）

不要：如图所示、念屏幕上的字、报文件名、念链接、说下一期、结尾报时长。一条口播尽量只留一个数字。

---

## 5. 单集目录与文件契约

```text
/workspace/.abroll-cloud/<集>/
├─ 项目说明.md
├─ 项目状态.json          # video_type=普通短视频
├─ script/voiceover.txt   # 整段口播原文
├─ script/phrases.txt     # 一行一条短语
├─ audio/vo-full.wav      # 整段配音
├─ audio/vo-align.txt     # 短语时间轴
├─ audio/bgm.wav          # 可选垫乐
├─ audio/sfx.wav          # 可选切镜音
├─ assets/                # A 卷：V-挥手 / V-正对讲 / V-摊手 / V-指向 / V-点赞 …
├─ plan/broll.json        # B 卷文案：tag / title / cards / punch
├─ plan/shot_recipe.json  # 可选：kind + phrases，尚无绝对时间
├─ timeline.json          # 锁定后的镜头表（有 start/end）
├─ broll/                 # 渲好的 B-*.mp4
├─ shots/                 # 切好的单镜（中间文件，勿进 成片/）
├─ output/                # 工程备份
└─ 00_最终成片_<名>.mp4
```

### `shot_recipe.json`（对齐前）

每镜：`id`、`kind`=`A|B`、`src`、`phrases[]`；开场近景可 `"close": true`。

### `timeline.json`（对齐后，组装只认这份）

- 成片规格：`size=[1080,1920]`，`fps=24`，`audio` 指向 `audio/vo-full.wav`
- `shots[]`：`id, kind, start, end, src, line`；A 可 `close`；B 的 `src` 在 `broll/`
- 可选：`a_caps`（A 卷圆角字幕）、`shutters`（色块快门）、`eyebrows`（A-ROLL / 编号）、`cover`、`bgm`
- `start/end` 必须铺满 `[0, duration]`，无缝无叠

### `plan/broll.json`

每条 B 镜一段文案（`file`/`tag`/`title`/`cards`/`punch`/`phrases`）。黑底卡从这里渲，不要手写烧进模型。

---

## 6. 组装（来自现网 `assemble.py`）

顺序：按 `timeline.json` 切镜 → concat → 叠字幕层 → 口播 + 垫乐 + 切镜音 → 写出 `00_最终成片_*.mp4`。

- A + `close`：放大再裁（约 `scale=1380:2454,crop=1080:1920:150:60`）
- 普通 A：略近（约 `scale=1188:2112,crop=1080:1920:54:105`）
- B：contain + pad 到 1080×1920
- 视频：H.264、yuv420p、CRF 18、24 fps；音频：AAC 44100
- 成片与 `项目说明.md` 必须在同一集目录

---

## 7. 接手检查

先读该集 `项目说明.md` 与 `项目状态.json`。已有产物不重做。两份文件冲突时先报告，不静默猜。`video_type` 必须是普通短视频。

---

## 8. 本简报读过的 Drive 笔记（最小集）

| 笔记 | Drive id | 用处 |
|------|----------|------|
| AI视频创作技能地图.md | `1r5RU7zp1Q36N4lHVl5Pt-bDq02iOHWia` | 分型：口播走短视频，不走短剧 |
| AI短视频制作工作流.md | `1i5SsHa0d3FyeUQD_eO1iEq6nOefXG4jr` | 七步生产 |
| AI项目归档与交付工作流.md | `1YwiUgtw5-KPEmNaDMRFhldviwvKNz15j` | 说明/状态/子目录；云端改写到本目录 |
| 本机公共路径与强制约束.md | `1uEDUG7SwSgulK92SI3d9W5VBfE2iPpXF` | 只取「知识视频不写 成片/」；本机 G: 落盘**不在云端执行** |
| 知识视频三步实操 / 项目说明.md | `1XrgE0lf0SWhmbR7DIclLoE0pPEed8SRv` | 三步定义 |
| 知识视频三步实操 / shot-list.md | `160KZWT-vXncXao9PIhBEAmxRuqIlPj4z` | 白底小灯 + 黑底图、生图不烧字 |
| 画面先于口播半拍 / shot_recipe.json | `1cQUzkg7JZXnXJSXRfAMT-gI912_Dcgh8` | A/B 镜头字段 |
| 画面先于口播半拍 / timeline.json | `1qbMcHqgKO4O6-R-ji3AtDsSlQ3Rp_uyp` | 对轴与快门 |
| assemble.py（多集同构） | 例 `19fKg8xvab1NWPtPTfzH5Mshu3tzYLbml` | 裁切、混音、成片名 |

检索时扫过大量 `render_broll.py`、剧情 EP、`.claim` 口播集，**未**把它们写成第二套管线。剧情笔记只用来排除。

同目录兄弟文件（不是本简报正文）：`topics.md`（本批选题）、`DELIVERY-TARGET.md`（若存在：只约束投递，不改本生产顺序）。
