# 云端成片投递目标（全体 sibling agents 必读）

更新：2026-09-11  
本文件只描述 **投递纪律**。不要把本目录或本文件上传到 Drive。

## 铁律：只在这台云端 Linux VM 上渲染

- **全部** ffmpeg / 生图 / 缓存 / 草稿 / 临时文件 **必须** 留在本 VM：
  - 工作区：`/workspace`
  - 临时与渲染缓存：`/tmp`（推荐 `/tmp/abroll-*`）
  - 本机草稿：`/workspace/.abroll-cloud/`（**禁止**上传）
- **禁止** 把任何路径写成或挂载到用户 Windows 盘：
  - 禁止 `C:\` `D:\` `G:\`
  - 禁止 `G:\成片` 这类「本地盘符」写法
  - 本 VM **不能、也不得** 挂载用户 PC 磁盘
- 用户口中的 `G:` 是他们电脑上的 **Google Drive for Desktop 同步盘**。  
  正确做法：用 **Google Drive MCP**（`Google-drive` namespace：`create_file` / `update_file` 等）把成片传到 Drive。  
  Drive Desktop **之后** 可能会把文件同步到他们的 `G:`——那是用户本机行为，**本机 agent 从未、也不得写 C/D/G**。

## VM 上的 `成片/` 只是中转

- `/workspace/成片/` = **staging only**（中转/待传）
- 渲染脚本把 **完成的** mp4 / 说明文档拷到这里即可
- **不要** 把 shots、broll、frames、cache、`.abroll-cloud` 草稿丢进 `成片/`
- 上传完成后，文件可以继续留在 staging，不必删

## Drive 投递目录（已存在，直接用）

| 项 | 值 |
| --- | --- |
| 文件夹名 | `云端成片-ArollBroll` |
| folderId | `1Ml9hbDKufpM-BT9qBciVdlOEJx_aq_yn` |
| 位置 | Google Drive **根目录**（My Drive） |
| 链接 | https://drive.google.com/drive/folders/1Ml9hbDKufpM-BT9qBciVdlOEJx_aq_yn |
| 创建约定 | 已有多个工程内「成片」子目录（课表/中科大/常用工程等），**不是**本流水线目标。记忆库（`Cursor记忆库`）只放文档，不放成片。因此在 Drive 根新建本文件夹。 |

上传时：`create_file` 设 `parentId = 1Ml9hbDKufpM-BT9qBciVdlOEJx_aq_yn`。  
二进制用 `base64Content` + `contentMimeType`（mp4=`video/mp4`）+ `disableConversionToGoogleType=true`。  
文本用 `textContent` + `contentMimeType`（如 `text/markdown`）+ `disableConversionToGoogleType=true`。

## 传什么 / 不传什么

**要传（成品）：**

- `/workspace/成片/` 下已完成的 `.mp4`
- 同目录成品说明：`.md` / `.txt` / `.pdf` / 封面图（若与成片配套）

**不要传：**

- `/workspace/.abroll-cloud/**`（含本文件、镜头、口播、中间帧）
- `/tmp/**` 里的 shots / broll / frames / cache
- 未完成、正在写入、或带 `.part` / `.tmp` 的文件
- 不要开新的仙侠/短剧渲染（除非用户明确点名）

## 操作顺序（渲染 agent）

1. 只在 `/tmp/...` 或 `/workspace/.abroll-cloud/<job>/` 渲染。
2. 成片稳定后，**复制**到 `/workspace/成片/<清晰文件名>.mp4`。
3. 投递 agent 用 Drive MCP 上传到上面的 folderId。
4. 在 `/workspace/.abroll-cloud/upload-log.jsonl` 记一行（sha256 + Drive fileId），避免重复上传。

## 给投递 / 上传 agent

- 先读本文件，不要新建第二个根目录成片夹（除非本夹失效）。
- 扫描 `/workspace/成片/`，跳过已在 `upload-log.jsonl` 且 sha256 未变的文件。
- 继续轮询：新文件出现再传。
- 回复用户时用中文：强调云端渲染、Drive 文件夹名/链接、以及 Drive Desktop 以后可能同步到 G:，但 agent 没写 C/D。

## 当前上传状态（2026-09-11 续传）

目标夹仍是 `云端成片-ArollBroll`（`1Ml9hbDKufpM-BT9qBciVdlOEJx_aq_yn`）。本轮只在本 Linux VM 操作，没有写 `C:\` / `D:\` / `G:\`。

**已在目标夹（不要重传）：**

| 文件 | Drive fileId | 备注 |
| --- | --- | --- |
| `INDEX.md` | `1O9IgN3im8M4O61Xlwu5MGZf4Px6n8SAp` | 文本 MCP 直传 |
| `00-深度工作总被打断.mp4` | `1OIlVUqGuVsjTWUlcVO3nSOcVccPI_aiq` | 从盘内旧成片 `copy_file`，3.6MB；VM QA 为 3.8MB |
| `01-口头答应没有截止日.mp4` | `1k30sQjDsHZpDzgeU3em0hc2Ub5E9cUAU` | 同上，2.7MB；VM QA 为 2.6MB |
| `05-先给选项再要决定.mp4` | `17IhQvg-f5x6-hldCMddj7cdxdl7Y9WPl` | 同上，2.5MB；VM QA 为 3.1MB |

**仍只在 VM `/workspace/成片/`，本轮未能把二进制送进目标夹：**

`02` `03` `04` `06` `07` `08` `09` `10` `11` 九条。Drive 全盘没有同名 / `00_最终成片_*` 可 `copy_file` 的副本。

失败原因（已核实）：

1. 官方 Google Drive MCP（`https://drivemcp.googleapis.com/mcp/v1`）只有 `create_file` 的 `base64Content` / `textContent`，没有 resumable / 本地路径 / 文件句柄。探测字段 `filePath` 被服务端拒成 `Unknown name "filePath"`。
2. `create_file` 整段 base64 会撑爆 agent 上下文（前序已 `resource_exhausted`），本轮按要求不再走这条。
3. MCP OAuth 在 Cursor 控制面，**没有**落到本 VM：无 `EXEC_DAEMON_MCP_OAUTH_*`、无 rclone.conf、无 ADC / service account、无 `gcloud`、Chrome 无登录态。Drive v3 `about` 无 token 返回 401。
4. 已安装 rclone 1.75.1 与 `google-api-python-client`，但没有可用 OAuth/SA，无法对 `https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable` 续传。

**跳过：** `仙侠云海突进.mp4`、草稿、`.abroll-cloud/**`。

要补传这 9 个二进制：在本 VM 提供 Drive 的 refresh token / rclone remote / service account（可写该 folderId），再用 rclone 或 Drive resumable API 直传文件，不要再经 MCP base64。
