# 一万日（kotoba） — 保守メモ

一人用の PWA。`index.html` 1 ファイルがアプリ本体で、GitHub Pages（https://yutatasaki.github.io/kotoba/）から配信する。データは本人の private リポジトリに JSON で置き、端末側は IndexedDB に持つ。ビルド工程はない。`index.html` を編集して `git push` すれば数十秒で反映される（Pages のキャッシュ対策として、アプリは起動時と復帰時に自分の更新を確認して自動で読み直す）。

- アプリ本体: `index.html`（HTML + CSS + JS）
- 3D 筋肉モデル: `assets/muscles.bin`（生成スクリプト `assets/build_muscles.py`）
- 仕様書: `ichimannichi_spec_*.md`, `kotoba_spec*.md`
- バックアップ置き場（ローカルのみ、git 管理外）: `backup/`

---

## 1. データの置き場所

| データ | 端末（IndexedDB `kotoba` / store `kv`） | リポジトリ | 内容 |
|---|---|---|---|
| 言葉（ノート） | key `notes:YYYY`（作成年ごと、全年を端末に保持）、未同期の年 `notesDirty`、最後に見た索引 `notesStamps` | `yutaTasaki/kotoba-data` の `notes/YYYY.json` と `notes/index.json` | 年ファイル方式のとき。旧方式では `data.json` の `notes` 配列 |
| ゴミ箱・下書き・API使用量・方式フラグ | key `data`（予備 `dataBackup`） | 同リポジトリ `data.json` | trash, drafts, usage, `journalMode`, `notesMode` |
| 記録（朝・相談・引く・問い） | key `journal:YYYY-MM`（月ごと）、索引 `journalIndex`、未同期の月 `journalDirty` | 同リポジトリ `journal/YYYY-MM.json` と `journal/index.json` | 月ファイル方式のとき。旧方式では `data.json` の `journal` 配列 |
| 筋トレ | key `training` | 同リポジトリ `training.json` | 日ごとの部位・種目・セット、種目→筋肉の対応 |
| 散歩 | key `walk`（予備 `walkBackup`） | `yutaTasaki/walk10000-data` の `data.json` | walk10000 と同じ形 |
| 設定（トークン・APIキー・モデル名・フラグ） | localStorage `kotoba_*` | 置かない | 端末ごと |

IndexedDB が使えない環境では同じキーが localStorage（`kotoba_kv_` 接頭辞）に落ちる。v6 より前の localStorage のコピー（`kotoba_data` など）は初回起動で IndexedDB に取り込んだあと、そのまま残してある（旧バージョンへ戻すときの保険。設定の「古い保存形式のコピーを消す」で消せる）。

### data.json の形（要点）

```
{ version: 2, updatedAt,
  notes: [ノート...]（旧方式のみ）, deletedIds[{id, deletedAt}]（旧方式のみ）, trash[note+deletedAt],
  journal: [...]（旧方式のみ）, deletedJournalIds[]（旧方式のみ）,
  drafts[], deletedDraftIds[], dismissedDuplicatePairs[], usage{deviceId:{label, months:{YYYY-MM:{kind:{calls,input,output,cacheWrite,cacheRead}}}}},
  journalMode: 'legacy' | 'monthly', journalModeAt, notesMode: 'legacy' | 'yearly', notesModeAt }
```

### ノート 1 枚の形

```
{ id: 'n_YYYYMMDD_連番', text, source, myWords, tags[], kind: 'quote'|'book'|'self', book?: {title, author},
  context?: [{text, at}]（周辺のメモ。モデルには渡さない）, links[{id, kind:'auto'|'manual', relation?, reason?}], rejectedLinks[],
  textHistory?[], myWordsHistory?[], video?{batchId,title,questionId,filmedAt}, autoLinkedAt, createdAt, updatedAt }
```

### 年ファイル `notes/YYYY.json`（作成年 = createdAt の年）

```
{ version: 1, year: 'YYYY', updatedAt, notes: [ノート...], deletedIds: [{id, deletedAt}] }
```

### 索引 `notes/index.json`

```
{ version: 1, updatedAt, years: { 'YYYY': { updatedAt, count } } }
```

端末は全年をメモリに持つ（網・相談・関連づけは全件を見る）。同期は「端末で触った年」「索引の updatedAt が変わった年」だけ取り直して PUT する。年ファイルの内容が変わらなければ索引の行も更新しない。

### 記録（journal）1 件の形

```
{ id: 'j_YYYYMMDD_連番', date: 'YYYY-MM-DD', kind: 'morning'|'consult'|'draw'|'question',
  text: 入力文, picks: [{ id: ノートid, why, hit?: 1, hitAt? }], closing, mood?(朝), sessionId?(引く),
  from[]/why_now/tension/for_viewer/used?(問い), createdAt, updatedAt }
```

`hit` が「刺さった ★」。ノート側には何も保存せず、回数はすべて journal から集計する。

### 月ファイル `journal/YYYY-MM.json`

```
{ version: 1, month: 'YYYY-MM', updatedAt, entries: [記録...], deletedIds: [{id, deletedAt}] }
```

### 索引 `journal/index.json`

```
{ version: 1, updatedAt, months: { 'YYYY-MM': { updatedAt, count,
    noteStats: { ノートid: { p: 届いた回数, h: ★の回数, q: 問いに使われた回数, last, lastHit } } } } }
```

全期間の「届いた回数・刺さった回数・問いに使われた回数」はこの索引だけで出す（月ファイルを全部読まない）。索引は月ファイルを書くたびにその月の行を作り直すので、壊れても月ファイルから復元できる（設定 →「記録を data.json 方式に戻す」→「月ファイル方式に移行」で作り直せる）。

### 筋トレ `training.json`

```
{ version: 1, updatedAt, days: [{ id: date, date, weight, parts: [{ part, exercises: [{ name, sets: [{ w, r, note?, drops?: [{w, r}] }], cardio?: {km, min, kcal, note} }] }], createdAt, updatedAt }],
  deletedDayIds[], exercises: { 部位: [{ name, lastUsedAt }] }, muscleMap: { 種目名: { p[], s[], at, by } } }
```

---

## 2. 同期の仕組み

- 変更のたびに 0.8 秒後に同期（`scheduleSync` → `syncNow`）。起動時・画面復帰時・オンライン復帰時にも同期。
- GitHub Contents API を PAT（`kotoba_ghToken`、両リポジトリの Contents: Read and write）で直接叩く。GET は `object` 形式で sha を取り、1 MB を超えるファイルは `raw` 形式で本文を取る（`ghGetContents`）。PUT は sha 付きで、409（他端末が先に書いた）なら取り直してマージしてもう一度。
- **言葉（年ファイル方式）**: `notesSyncNow`。`notes/index.json` を取得 → 対象の年（端末で変更した年、他端末が更新した年、端末に無い年）を 1 つずつ取得 → `mergeNoteSets`（id ごとに `updatedAt` の新しい方、削除は墓標の時刻と比較）→ 内容が変わっていれば PUT → 索引を PUT。端末側は `saveData` のたびに年ごとの JSON を前回と比較し、変わった年だけ IndexedDB に書いて「未同期」にする（`persistNoteYears`）。
- **data.json**: ゴミ箱・下書き・使用量・方式フラグ。取得 → `mergeData` → PUT。旧方式ではここにノートと記録も入る。
- すべての GitHub 呼び出しは 30 秒でタイムアウトし（`ghFetch`）、エラーとして次回の同期でやり直す。
- **記録（月ファイル方式）**: `journalSyncNow`。索引を取得 → 対象の月（今月・先月・端末で編集した月・他端末が更新した月）を 1 つずつ取得 → `mergeJournalSets` でマージ → 内容が変わっていれば PUT → 索引を PUT。端末のメモリ（`data.journal`）には今月・先月と、記録タブや詳細で開いた月だけが載る。
- **筋トレ**: `training.json`、日ごとに `updatedAt` 新しい方＋墓標、種目カタログと筋肉対応は和集合。
- **散歩**: walk10000 と同じ「歩いた日数が多い方が勝つ」ファイル単位のルール。
- 同期バーの文言: `renderSyncBar`。エラーは localStorage の `kotoba_lastSyncError` などに残り、設定の「最終同期エラー」に出る。

---

## 3. 主要な定数の場所（index.html 内、検索で飛べる）

| 何 | 検索する文字列 |
|---|---|
| リポジトリ名・ファイル名 | `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_PATH`, `TRAINING_PATH`, `JOURNAL_INDEX_PATH`, `NOTES_INDEX_PATH` |
| GitHub の待ち時間 | `GH_TIMEOUT_MS`（30 秒） |
| 候補の言葉の上限・選び方 | `DEFAULT_COMPRESS_THRESHOLD`（200）, `selectCandidateNotes` |
| 種類の一覧・推定 | `NOTE_KINDS`, `inferNoteKind` |
| 読書メモのプロンプト | `buildReadingSystemBlocks` |
| 端末保存のキー | `KV_DB_NAME`, `STORAGE_KEY`, `BACKUP_MAX_CHARS` |
| 刺さった★の重み（減衰・飽和・休み・探索） | `HIT_TUNING` |
| 問いの角度・材料 | `QUESTION_MODES`, `buildQuestionSystemBlocks` |
| 相談・朝のプロンプト | `buildChatSystemBlocks` |
| 自動関連づけのプロンプト | `buildAutoLinkSystemBlocks` |
| 筋肉対応のプロンプト | `buildMuscleSystemBlocks` |
| モデル名の既定値 | `DEFAULT_AUTOLINK_MODEL`, `DEFAULT_CHAT_MODEL` |
| API の max_tokens | 各 `fetch('https://api.anthropic.com` の `max_tokens` |
| 使用量の単価 | `MODEL_PRICING` |
| 筋トレ画像のデザイン | `trLayout`, `trDrawPage`（`TR_GREEN` など） |
| 3D の色・モデル URL | `MUSCLE_COLORS`, `MUSCLE_BIN_URL`, `THREE_MODULE_URL` |
| 筋肉一覧 | `MUSCLE_CATALOG`（`assets/muscles.json` と同じ） |
| 網の見た目 | `GRAPH_FIT_FLOOR`, `graphPathsFrom` |

---

## 4. 困ったときの戻し方

### 4.1 まずバックアップ

```
git clone https://github.com/yutaTasaki/kotoba-data.git   backup-kotoba-data
git clone https://github.com/yutaTasaki/walk10000-data.git backup-walk10000-data
```
（`git` が無ければ GitHub の各リポジトリ → Code → Download ZIP でも同じ。）どちらも履歴を持つので、`git log` で任意の時点の `data.json` を取り出せる。アプリの設定 →「言葉のデータをエクスポート」でも端末上の data.json を保存できる。

### 4.2 記録を月ファイルから data.json に戻す（旧方式へ）

設定 → 同期 →「記録を data.json 方式に戻す」。全月を読み込んで `data.json` の `journal` に書き戻し、`journalMode` を `legacy` にする。月ファイルは残るが使われない。これで v6 より前の `index.html` でも動く状態になる。

### 4.2b 言葉を年ファイルから data.json に戻す（旧方式へ）

設定 → 同期 →「言葉を data.json 方式に戻す」。全年を読み込んで `data.json` の `notes` に書き戻し、`notesMode` を `legacy` にする。年ファイルは残るが使われない。v7.2 より前の `index.html` に戻す前に必ず実行する。

### 4.3 アプリを前のバージョンに戻す

```
git log --oneline            # 戻したいコミットを探す
git checkout <コミット> -- index.html
git commit -m "revert index.html"
git push
```
主な節目: `7bff371`（v7.1 読書メモ、年分割の前）, `17f53d6`（v7.0 種類）, `1773083`（v6.0 IndexedDB + 月ファイル）, `bd77edb`（容量対策の前の最終形 + 保存ガード）, `5607b73`（3D 筋肉 v5.1）。
月ファイル方式のまま v6 より前へ、年ファイル方式のまま v7.2 より前へ戻すと記録・言葉が見えなくなるので、先に 4.2 / 4.2b を実行すること。

### 4.4 ある日の data.json に戻す（リポジトリ側）

```
cd backup-kotoba-data
git log --oneline -- data.json
git show <コミット>:data.json > data.json    # 取り出す
git add data.json && git commit -m "restore" && git push
```
アプリ側は次の同期でマージする。「端末の方が新しい」と判断された項目は端末の内容が勝つので、完全に戻したいときは端末の設定 →「古い保存形式のコピーを消す」→ ブラウザの IndexedDB（サイトデータ）も消してから起動する。

### 4.5 端末のデータを消して入れ直す

iPhone: 設定 → Safari → 詳細 → Web サイトデータ → yutatasaki.github.io を削除。次回起動で空になり、同期で全部戻る（「端末が空でリポジトリにデータがある」場合は上書きしないよう、取り込みだけ行う）。

---

## 5. よくある不具合と直し方

| 症状 | 見る所 | 直し方 |
|---|---|---|
| 同期バーが「エラー」 | 設定 → 最終同期エラー | 401/403 はトークン切れ → 新しい PAT を入力。404 はリポジトリ名/パス。409 が続くときは「今すぐ同期」をもう一度。 |
| 「端末の保存に失敗しました」 | 設定 → データ量 | IndexedDB が満杯かプライベートモード。サイトデータを整理する。クラウドには同期されているので消えない。 |
| 朝の言葉・相談が「応答が長すぎて途中で切れました」 | 設定 → 最終エラー | `max_tokens` を増やす（`fetch('https://api.anthropic.com` を検索）。thinking を含むモデルは 8192 以上。 |
| API が 429 | 少し待つ。連続で出るなら `sleep(2000)` の再試行間隔を伸ばす。 |
| 言葉が消えたように見える（年ファイル方式） | 設定 → 言葉の保存方式 | 「年ファイル（N 年分、未同期 M）」を確認。0 年分なら索引が取れていない → 「今すぐ同期」。それでも空なら 4.2b → 移行で作り直す。端末の年ファイルはリポジトリの `notes/YYYY.json` と同じ内容。 |
| 同期が「同期中…」のまま長い | 設定 → 最終同期エラー | v7.2 から 30 秒でタイムアウトしてエラーになる。旧方式で全件を送っていると 1 回の PUT が数秒かかる（年分割で解消）。 |
| 月ファイルに記録が出ない | 設定 → 記録の保存方式 | 「月ファイル（N か月、読み込み中 M か月）」を確認。0 か月なら索引が無い → 4.2 → 移行で作り直す。 |
| ★の回数が合わない | `journal/index.json` | 月ファイルが正。4.2 → 移行で索引を作り直す。 |
| 3D が表示されない | 設定 → 最終エラー（筋肉3D） | jsdelivr（three.js）か `assets/muscles.bin` が取れていない。オンラインで再試行。 |
| 網が真っ暗/中心が外れる | 端末の幅 | `GRAPH_FIT_FLOOR` と `graphViewport` の高さ（CSS `60vh`）。 |
| 画面が更新されない（古いまま） | Pages のキャッシュ | 一度閉じて開き直す。`checkForUpdate` が `?v=` 付きで読み直す。 |
| iPhone で入力途中の筋トレが消えた | | v4.1 以降は自動保存。設定 → 最終同期エラーを確認。 |

---

## 6. 開発のしかた（自分で直すとき）

1. `index.html` を編集する（1 ファイル）。
2. 文法チェック: `<script>` 内を抜き出して `node --check`。
   ```
   node -e "const s=require('fs').readFileSync('index.html','utf8');const a=s.indexOf('<script>\n(async () => {');const b=s.lastIndexOf('</script>');require('fs').writeFileSync('app.js',s.slice(a+8,b))" && node --check app.js
   ```
3. ローカルで見る: `npx http-server -p 8731`（または任意の静的サーバー）で `http://localhost:8731/`。
4. `git commit` → `git push`。Pages 反映は 30〜60 秒。
5. 本番の同期を壊さずに試したいときは、GitHub API を差し替えたテスト版が作れる（`_test_index.html`：fetch を横取りしてメモリ上の偽リポジトリに読み書きする。作り方はこの README の末尾）。

### テスト版の作り方（偽 GitHub）

`index.html` の `<script>\n(async () => {` の直前に、`fetch` を差し替えるスクリプトを挟んだコピーを `_test_index.html` として置く（`api.github.com/repos/.../contents/...` への GET/PUT をメモリ上の `{sha, text}` で応える。PUT は sha が違えば 409）。localStorage の `kotoba_ghToken` に何か入れれば同期が走る。`_` で始まるファイルはコミットしない。

---

## 7. ライセンス表記

- 3D モデル: BodyParts3D, © The Database Center for Life Science, CC BY 4.0（広背筋・腹直筋は皮膚表面からの近似）。
- フォント: DotGothic16（Google Fonts）。
- three.js（MIT、jsdelivr から読み込み）。

---

## 8. 次の壁（時期の目安と、そのとき何をするか）

| 壁 | 目安 | 何が起きるか | 対策 |
|---|---|---|---|
| ノートが **600 枚**（data.json 約 2 MB） | — | v7.2 で年ファイル方式を実装済み（設定 →「言葉を年ファイル方式に移行」）。同期で送るのは触った年の分だけ | 移行後は 1 年分（≈1 MB/年）が 1 ファイルの上限。年間 1,000 枚を超えるなら `notesYearPath` を半年や四半期に変える（`yearOfNote` の粒度を変えるだけ） |
| 候補の言葉の上限（既定 200 枚） | 2027 年初め | 200 枚を超えると、相談・自動関連づけは全件ではなく「入力に近い言葉」を端末で選んで渡す（`selectCandidateNotes`）。全件をキャッシュしていた頃より 1 回あたり約 3 倍のトークン（Sonnet で $0.03/相談） | そのまま使える。精度が足りないと感じたら `selectCandidateNotes` のスコア（2-gram 重なり・タグ・種類・★の重み・新しさ）を調整。将来 embedding に替えるならこの関数だけ差し替える |
| API の月上限（既定 $2） | 読書メモを使い始めたら | 読書メモ 1 回 ≈ $0.01〜0.015（Sonnet の分解＋Haiku の関連づけ）。1 日 10 回で **月 $4〜5** | 設定 → Claude API → 月の上限を $10 程度に上げる。超えると自動関連づけと朝の言葉が止まる |
| 相談のノート一覧が「静かに古い 400 件で止まる」 | — | v7.0 で解消済み（上の候補選びに置き換えた） | — |
