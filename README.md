# 一万日（kotoba） — 保守メモ

このファイルは、作った本人（と、手伝う人）が **あとから自分で直す・戻す** ためのメモです。前半は「困ったときにどうするか」、後半は「中身がどうなっているか」。急いでいるときは **第1章と第2章だけ** 読めば足ります。

- アプリの URL: https://yutatasaki.github.io/kotoba/
- アプリ本体: このリポジトリ（`yutaTasaki/kotoba`）の `index.html` 1 ファイル。`git push` すると 1 分ほどで反映される。
- データ（自分の言葉・記録など）: 別の非公開リポジトリ `yutaTasaki/kotoba-data` と `yutaTasaki/walk10000-data` に JSON で置く。**アプリを消してもデータはここに残る。**
- 端末（iPhone・PC のブラウザ）にも同じデータのコピーがあり（IndexedDB という保存領域）、起動時と操作のたびにリポジトリと同期する。

用語:
- **リポジトリ**: GitHub 上のフォルダのようなもの。履歴（いつ何を変えたか）が全部残る。
- **PAT（トークン）**: GitHub がアプリに読み書きを許可するための長い文字列。設定画面に入れる。有効期限がある。
- **同期**: 端末のデータとリポジトリのデータを突き合わせて、新しい方に揃えること。
- **IndexedDB**: ブラウザの中の保存領域。iPhone の「Web サイトデータ」を消すと消える（リポジトリから戻る）。

---

## 1. 困ったときの対処（症状から引く）

| 症状 | まず見る所 | 対処 |
|---|---|---|
| 画面上の同期バーが赤い「エラー」 | 設定 →「最終同期エラー」 | 文中の数字で判断。**401 / 403** = トークンが切れた → 2.1。**404** = リポジトリ名かファイル名が違う（ふつう起きない）。**409** が続く = 2 台が同時に書いた → 「今すぐ同期」をもう一度。**timeout** = 回線が止まった → 電波の良い所で「今すぐ同期」。 |
| 同期バーが「同期中…」のまま長い | そのまま 30 秒待つ | 30 秒で自動的にエラーに変わり、次の同期でやり直す。何度も出るなら回線。 |
| 「端末の保存に失敗しました」 | 設定 →「データ量」 | 端末の保存領域がいっぱいか、プライベートブラウズ。iPhone の「Web サイトデータ」を整理する。リポジトリには同期済みなので消えない。 |
| 言葉が減った・消えたように見える | 設定 →「言葉の保存方式」 | 「月ファイル（N か月分）」の N が 0 なら索引が取れていない → 「今すぐ同期」。直らなければ 2.4。 |
| 記録（朝・相談・引く・問い）が消えたように見える | 設定 →「記録の保存方式」 | 「月ファイル（N か月）」の N が 0 なら → 「今すぐ同期」。直らなければ 2.4。 |
| ★（刺さった）の回数が合わない | — | 2.4 の「記録を data.json 方式に戻す → 月ファイル方式に移行」で索引を作り直す。 |
| 相談・朝の言葉が失敗する | 画面に出る文、設定 →「最終エラー」 | v9.5 から理由が分かれて出る。「API キーが使えません（401）」= 設定でキーを入れ直す。「混みあっています（429）」= 少し待つ。「リクエストが受け付けられませんでした（400）」= 設定のモデル名（最終エラーに応答の本文が出る）。「時間がかかりすぎました（60秒）」= 回線かモデルの混雑。「通信できませんでした」= 電波。「応答を読み取れません」= もう一度（最終エラーに応答の冒頭が残る）。上限に達しているときは相談画面の入力欄の下に先に出る。 |
| 筋トレの入力欄をタップするとキーボードが閉じる | — | v9.6 で修正。裏の同期が終わると画面を描き直していて、入力中でも作り直されてフォーカスが外れていた。入力中（`isTypingInApp`）は描き直さない。 |
| 朝の言葉・相談で「応答が長すぎて途中で切れました」 | 設定 →「最終エラー」 | もう一度試す。毎回出るなら 4.2 の `max_tokens` を増やす。 |
| API が「429」 | — | 使いすぎ。少し待つ。 |
| 朝の言葉が出ない・自動関連づけが止まった | 設定 →「API使用量」 | 月の上限（USD）を超えると止まる。上限を上げる。 |
| 3D の筋肉が出ない | 設定 →「最終エラー」 | ネットが必要（three.js とモデルを読む）。オンラインで開き直す。 |
| 画面が古いまま（直したはずの所が直っていない） | — | アプリを完全に閉じて開き直す。それでも古ければ iPhone の設定 → Safari → 詳細 → Web サイトデータ → yutatasaki.github.io を削除（データはリポジトリから戻る。トークンと API キーは入れ直し）。 |
| 下のタブバーがスクロール中に浮く | — | v7.3 で修正済み。まだ出るなら上の「画面が古いまま」を試す。 |
| 入力途中の文章が、他のアプリに切り替えて戻ると消えている | — | v7.5 で対応。入力中の内容は 0.3 秒ごと・画面を離れるとき・バックグラウンドになるときに端末に退避し、次に開いたときにその画面と内容を復元する（48 時間以内）。保存・送信・「戻る」で消える。localStorage の `kotoba_inputDraft`。 |
| 筋トレの入力途中で消えた | 設定 →「最終同期エラー」 | v4.1 から自動保存。エラーが無ければ同期で戻っている。 |
| 「1年前」「どこかの日」で記録のある日が開かない | 記録タブの月ラベル「（読み込み中）」 | 端末に無い月の記録（朝・相談・引く・問い）は開いた時に 1 ファイル読む。圏外なら散歩・筋トレ・瞑想・言葉だけ出る。「一番近い日」の探索は端末が知っている日（散歩・筋トレ・瞑想・言葉の作成日・読み込み済みの月）だけを見る。 |
| 別のタブから戻ると「設定」タブになっている | — | v9.2 で修正。設定画面の入力欄（モデル名・上限・散歩の日付）は常に値が入っているため、設定を一度開くだけで「入力の退避」が設定画面の下書きとして 48 時間残り、読み込み直すたびにそこへ飛んでいた。設定画面は退避の対象から外し、30 分より古い下書きは起動時に画面を飛ばさないようにした。 |
| 撮るのデッキが他の端末に出てこない | 撮る画面の「最終同期」 | 作った側は 0.8 秒後に自動で送る。受け取る側は起動・タブに戻る・オンライン復帰のときだけ取りに行くので、**開きっぱなしのタブは自分から取りに行かない**。撮る画面の「取り込む」を押す。同じデッキを 2 台で同時に編集すると、後に保存した側が丸ごと勝つ（カード単位では混ざらない）。 |
| 撮るで貼った JSON が取り込めない | 撮る画面の貼り付け欄の下の文言 | 「JSON として読めませんでした」= チャットの返事に説明文が混じっている。JSON の部分（`{` から `}`）だけを貼る。コードブロックの ``` は付いたままでよい。URL が消えた場合は http/https でなかったため（意図した動き）。 |
| 瞑想のタイマーが鳴らない | — | ホーム画面のアプリは画面が消えると止まる。計測中は画面を消さない（v8.0 は Wake Lock で消えないようにする）。iOS 純正のタイマーを使い「後から入れる」で記録してもよい。鳴らなくても開始時刻は端末に残るので、戻ると分数は正しく出る。 |
| 瞑想の記録が減った・消えたように見える | 設定 →「瞑想の保存方式」 | 「年ファイル（N 年分）」の N が 0 なら索引が取れていない → 「今すぐ同期」。 |
| 読書メモの「分解する」が失敗 | 一括入力の画面の文言、設定 →「最終エラー」 | v7.4.1 から理由が出る。「API エラー 429」= 混雑、少し待つ。「API エラー 401」= API キー。「時間切れ」= 文章を短く分ける（120 秒で打ち切り）。「応答を JSON として読めません」= もう一度（応答の先頭が文言に出る）。「途中で切れました」= 文章を分ける。 |

---

## 2. 戻し方（手順を省略せずに）

### 2.1 トークン（PAT）を作り直す

1. PC で GitHub にログイン → 右上のアイコン → **Settings** → 左の一番下 **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**。
2. Token name は何でもよい（例 `kotoba`）。Expiration は最長（1 年）にする。
3. **Repository access** → **Only select repositories** → `kotoba-data` と `walk10000-data` の 2 つを選ぶ。
4. **Permissions** → **Repository permissions** → **Contents** を **Read and write** にする。他は触らない。
5. **Generate token** → 表示された `github_pat_…` をコピー（この画面を閉じると二度と見られない）。
6. アプリの設定 → 1. 同期 → 入力欄に貼って **保存** → 「今すぐ同期」。同期バーが「同期済み」になれば完了。
7. iPhone と PC の両方で 6 を行う（トークンは端末ごとに入れる）。

### 2.2 まずバックアップ（何かを戻す前に必ず）

PC で（Git が入っていれば）:
```
git clone https://github.com/yutaTasaki/kotoba-data.git   backup-kotoba-data-YYYYMMDD
git clone https://github.com/yutaTasaki/walk10000-data.git backup-walk10000-data-YYYYMMDD
```
Git が無ければ、ブラウザで GitHub の各リポジトリを開き **Code（緑のボタン）→ Download ZIP**。
加えてアプリの設定 → 5. データ →「言葉のデータをエクスポート」で、端末上のデータも 1 部保存しておく。

### 2.3 ある日の状態にデータを戻す（リポジトリの履歴から）

リポジトリには変更のたびの履歴が残っている。例えば「昨日の朝の状態の `data.json`」に戻すには:
```
cd backup-kotoba-data-YYYYMMDD
git log --oneline -- data.json            # 履歴一覧。左の 7 文字が「コミット」
git show <コミット>:data.json > data.json  # その時点の内容を取り出す
git add data.json
git commit -m "restore data.json"
git push
```
年ファイル・月ファイルも同じ（`notes/2026.json`, `journal/2026-09.json` など。ファイル名を変えるだけ）。
Git を使わない場合: GitHub でファイルを開く → **History** → 戻したい日時を選ぶ → 右上の **…** → **View file** → 内容をコピーして、現在のファイルを **Edit** で貼り替えて **Commit changes**。

そのあと、アプリ側:
- 端末はまだ新しい内容を持っているので、そのまま同期すると「端末の方が新しい」項目は端末が勝つ。
- 完全に戻したいときは、**端末側を空にしてから**起動する（iPhone: 設定 → Safari → 詳細 → Web サイトデータ → yutatasaki.github.io を削除。PC Chrome: アドレスバー左の鍵アイコン → サイトの設定 → データを削除）。空の端末はリポジトリの内容をそのまま取り込む。
- トークンと API キーも消えるので、2.1 の 6 と設定の API キーを入れ直す。

### 2.4 保存方式を戻す（月ファイルをやめる）

「言葉」と「記録」は、それぞれ **旧方式（data.json に全部入り）** と **新方式（月ごとのファイル）** を設定画面のボタンで行き来できる。どちらも片道切符ではない。

- 設定 → 1. 同期 →「**言葉を data.json 方式に戻す**」: 全月のファイルを読み込み、`data.json` に書き戻す。月ファイルは残るが使われない。
- 設定 → 1. 同期 →「**記録を data.json 方式に戻す**」: 全月のファイルを読み込み、`data.json` に書き戻す。
- 逆（新方式へ）は同じ場所の「…方式に移行」。移行は最後に `data.json` を書き換えるので、途中で失敗しても旧方式のまま使える。
- 実行前に 2.2 のバックアップ。実行中は画面を閉じない。1 台で実行すれば、もう 1 台は次の同期で自動的に同じ方式に切り替わる。

### 2.5 アプリ（index.html）を前のバージョンに戻す

```
cd kotoba                      # このリポジトリ
git log --oneline              # 履歴。左の 7 文字がコミット
git checkout <コミット> -- index.html
git commit -m "revert index.html"
git push
```
1 分ほどで反映。主な節目（新しい順）:

| コミット | 内容 |
|---|---|
| `a77c11e` | v7.4 言葉を月ファイルに（年ファイルから自動切替）、言葉タブ 200 枚ずつ表示 |
| `e447aa2` | v7.3 タブバーが浮く不具合の修正（ページ固定 + `#shell` スクロール） |
| `521a963` | v7.2 言葉の年ファイル、引くの★、30 秒タイムアウト |
| `7bff371` | v7.1 読書メモ |
| `17f53d6` | v7.0 種類（名言/本/自分）、候補の言葉の選び方 |
| `1773083` | v6.0 IndexedDB 保存、記録の月ファイル |
| `bd77edb` | v6 の直前（localStorage 保存、data.json 全部入り） |

**注意**: 言葉が月ファイル方式のまま v7.4 より前へ（`e447aa2` 以前は年ファイル、`521a963` より前は data.json しか読めない）、記録が月ファイル方式のまま `1773083` より前へ戻すと、そのアプリはファイルを読めず言葉・記録が見えなくなる。**先に 2.4 で旧方式に戻してから**アプリを戻すこと。

### 2.6 端末のデータを消して入れ直す

iPhone: 設定 → Safari → 詳細 → Web サイトデータ → yutatasaki.github.io を削除 → アプリを開く → トークンと API キーを入れる → 同期で全部戻る。
（「端末が空でリポジトリにデータがある」ときは、端末の空データで上書きしないよう、取り込みだけ行う。）

---

## 3. 中身の説明

### 3.1 データがどこに、どんな形であるか

| データ | 端末（IndexedDB `kotoba` / store `kv`） | リポジトリ | 備考 |
|---|---|---|---|
| 言葉（ノート） | `notes:YYYY-MM`（作成月ごと。全月を端末に持つ）、未同期の月 `notesDirty`、最後に見た索引 `notesStamps` | `kotoba-data` の `notes/YYYY-MM.json` と `notes/index.json` | 月ファイル方式のとき。旧方式では `data.json` の `notes`。v7.2〜7.3 の年ファイル `notes/YYYY.json` は v7.4 で自動的に月ファイルへ移され、残骸として残る |
| ゴミ箱・下書き・API使用量・方式フラグ | `data`（予備 `dataBackup`） | `kotoba-data` の `data.json` | |
| 記録（朝・相談・引く・問い） | `journal:YYYY-MM`（月ごと）、索引 `journalIndex`、未同期の月 `journalDirty` | `kotoba-data` の `journal/YYYY-MM.json` と `journal/index.json` | 月ファイル方式のとき。旧方式では `data.json` の `journal` |
| 筋トレ | `training` | `kotoba-data` の `training.json` | |
| 瞑想 | `meditation:YYYY`（年ごと。全年を端末に持つ）、未同期の年 `meditationDirty`、最後に見た索引 `meditationStamps` | `kotoba-data` の `meditation/YYYY.json` と `meditation/index.json` | v8.0。最初から年ファイル |
| 散歩 | `walk`（予備 `walkBackup`） | `walk10000-data` の `data.json` | walk10000 と同じ形 |
| 設定（トークン・APIキー・モデル名・各種フラグ） | localStorage `kotoba_*` | 置かない | 端末ごと |

IndexedDB が使えない環境では同じキーが localStorage（`kotoba_kv_` 接頭辞）に入る。v6 より前の localStorage のコピー（`kotoba_data` など）は初回起動で取り込んだあと残してある（旧バージョンへ戻すときの保険。設定の「古い保存形式のコピーを消す」で消せる）。

**data.json**
```
{ version: 2, updatedAt,
  notes: [...]（旧方式のみ）, deletedIds: [{id, deletedAt}]（旧方式のみ）, trash: [ノート + deletedAt],
  journal: [...]（旧方式のみ）, deletedJournalIds: []（旧方式のみ）,
  drafts: [], deletedDraftIds: [], dismissedDuplicatePairs: [],
  usage: { 端末id: { label, months: { 'YYYY-MM': { 機能: {calls, input, output, cacheWrite, cacheRead} } } } },
  journalMode: 'legacy'|'monthly', journalModeAt, notesMode: 'legacy'|'monthly'（'yearly' は v7.2 の名残。起動時に 'monthly' へ自動変換）, notesModeAt }
```

**ノート 1 枚**
```
{ id: 'n_YYYYMMDD_連番', text, source, myWords, tags: [], kind: 'quote'|'book'|'self', book?: {title, author},
  keep?: 1（「残したい」の印。普通は項目なし）, lastViewedAt?（一覧の「眠っている順」から詳細を開いた最終日時。眠り順の計算にだけ使う）,
  context?: [{text, at}]（周辺のメモ。AI には渡さない）,
  links: [{id, kind: 'auto'|'manual', relation?: 'similar'|'opposite'|'supplement', reason?}], rejectedLinks: [],
  textHistory?: [], myWordsHistory?: [], video?: {batchId, title, questionId, filmedAt}, autoLinkedAt, createdAt, updatedAt }
```

**月ファイル `notes/YYYY-MM.json`**（作成月 = createdAt の年月。削除の墓標は id の日付から）
```
{ version: 1, month: 'YYYY-MM', updatedAt, notes: [...], deletedIds: [{id, deletedAt}] }
```
**索引 `notes/index.json`**: `{ version: 1, updatedAt, months: { 'YYYY-MM': { updatedAt, count } } }`
1 ファイルは 1 か月分なので、読書が多い月でも 1 MB 程度で頭打ち。分割の判断や操作は要らない。

**記録 1 件**
```
{ id: 'j_YYYYMMDD_連番', date: 'YYYY-MM-DD', kind: 'morning'|'consult'|'draw'|'question'|'read'（read = 言葉の詳細で押した★。届いた回数には数えない）|'deck'（撮るのデッキ）,
  text: 入力文, picks: [{ id: ノートid, why, hit?: 1, hitAt? }], closing, mood?（朝）, sessionId?（引く）,
  from[] / why_now / tension / for_viewer / used?（問い）, scene / ask / core / sides{a,b} / qtype（v8.3〜8.4 の問い：場面の1文・そこに立てる問い・材料の言い回しを残した芯・場面の両側・型。text は scene + ask。古い問いは scene が空で text が問い）, createdAt, updatedAt }
```
`hit` が「刺さった ★」。ノート側には何も保存せず、回数は記録から集計する。`use` は v8.5 の「使う」印の名残。v8.7 で撮るのデッキ内の相談に置き換わったので、読み込みでは保持するが使っていない（消すと古い版の端末とのマージで往復するため残す）。

**デッキ 1 件（撮る。kind: 'deck'）**
```
{ id, date, kind: 'deck',
  hook: 入り（0秒で言う1行。断言か問いかけ）,
  text: 仮の答え（1文。空のあいだはカードを足せない）, title: 動画のタイトル（任意）,
  questionId: 元の問いの記録 id（手書きなら ''）, questionText: 問いの写し, from: [材料の言葉 id],
  cards: [{ id: 'c1', kind: 'research'|'fun'|'word'|'record',
            slot: 1〜7（話の型の枠）, stance: 'support'|'break'|''（事実が仮の答えを支持するか壊すか）, gen: 1（貼り込んだカード。引き直しはこれだけを不採用にする）,
            label: 撮影表示に出る手がかりの一行（10〜15字。生成の JSON に含めさせ、取り込んだあと手で直す）,
            detail: 数字・手法・対象人数（撮影中は詳細を開いたときだけ出る）,
            flow: 直前のカードとの関係（展開の取り込み。編集画面にだけ出る）,
            fact: 聞く人に向けた1文（40字まで。著者名・手法・変数名を入れない）, source: 媒体・年・著者, url, breaks: 仮の答えの何を壊すか,
            tag?: '伝承'|'噂'（わくわくのみ）, belief?: 'yes'|'half'|'fun'（自分が信じているか）,
            noteId?（言葉カード）, order, dropped }],
  flowNote: 流れの説明（撮る前に一度読む文。撮影表示には出さない）,
  consult: { input: 相談に投げた文, at, picks: [{ id, why }] } | null（デッキの中で相談したときだけ。会話本文は保存しない）,
  premises: [仮の答えが立つための前提], conflicts: [{ premise, cardId, what }]（「答えを壊す」の結果）,
  answers: [{ text, at, stage: 'first'|'revised'|'after' }]（仮の答えの履歴。1 分以内の編集は同じ行を上書き）,
  status: 'draft'|'shot', shotAt, picks: [], createdAt, updatedAt }
```
**流れの説明（v9.4）**：撮る前に一度読んで全体の転がり方を頭に入れるための 300〜500 字。プロンプトをコピーしてチャットに貼り、返ってきた文をそのまま欄に貼る（JSON ではないので取り込みボタンは無い）。プロンプトは「カードの事実を繰り返さない・数字や固有名詞を書かない・カードからカードへの動きと落差だけ・喋る言い回しや指示を書かない」で縛ってある。**撮影表示には出さない**（読める文が手元にあると台本になる）。撮影表示を開くと、この文だけが先に全画面で出て、「読んだ」でカードに変わる。同じデッキではその起動中は一度だけ。

**撮影表示（v9.2）**：カンペなので 1 枚 1 行。番号・★（壊すの枠）・`label`・出典の略だけを出す。`breaks` は出さない。タップでその 1 枚だけ詳細が開き（`fact` → `detail` → 出典・種別・信じ度 → 出典を開く）、長押し（0.5 秒）で話し終えた印として薄くなる。`flow`（展開）はカードの中ではなく**カードとカードの間**に細い 1 行で出る（前から次への移り方なので行の間が自然）。`label` が空のカードは `fact` の先頭 15 字を暫定表示し、開くときに未記入の枚数を知らせる。ラベルは生成の JSON に含めさせて取り込み、編集画面で直す（空から 10 枚書くより速い）。編集画面の「ラベルだけ書く」で、番号と色と 1 行入力だけを並べて直せる。

**編集画面の並び（v9.4）**：上から順に埋めれば完成する順。1 問い → 2 仮の答え → 3 タイトル → 4 相談 → 5 カード → 6 答えを壊す → 7 展開 → 8 入り → 9 流れの説明。まだ使えないブロックはボタンを薄くして理由を 1 行だけ出す（`shootGate`。「カードが3枚そろうと使えます。（いま 1枚）」など）。「答えを壊す」の結果の下に仮の答えをもう一度置いてあり、上の欄と同じ内容を書き直せる（両方向に同期）。

**話の型**：入り → 先出し（仮の答え） → 支え → 寄り道 → 壊す → 言葉 → 言い直し の 7 枠で固定。答えを先に言い、支えて、壊して、言い直す形。カードは枠（`slot`）に割り当てられ、撮影表示は作成順ではなく枠の順に出す。枠の定義は `TALK_SLOTS` の配列 1 か所（名前・説明・受け入れる種類・並び）。枠 1・2・7 はカードを持たない。`slot` はカードに保存されるので、既存の番号の意味を変えないこと（追加は末尾）。第1段のデッキ（`slot` なし）は読み込み時に種類ごとの既定（研究・記録 3／わくわく 4／言葉 6）が入る。

カードは材料であって台本ではない。第1段では AI を通さず、言葉カードは相談の「使う」印から、記録カードはその日の朝の記録から作り、研究・わくわくは手で書く（第2段で web search 付きの生成に置き換える）。

**月ファイル `journal/YYYY-MM.json`**: `{ version: 1, month, updatedAt, entries: [...], deletedIds: [] }`
**索引 `journal/index.json`**: `{ version: 1, updatedAt, months: { 'YYYY-MM': { updatedAt, count, noteStats: { ノートid: { p: 届いた回数, h: ★の回数, q: 問いに使われた回数, last, lastHit } } } } }`
全期間の「届いた回数・刺さった回数・問いに使われた回数」はこの索引だけで出す。索引は月ファイルを書くたびに作り直すので、壊れても月ファイルから復元できる（2.4）。

**筋トレ `training.json`**
```
{ version: 1, updatedAt, days: [{ id: 日付, date, weight, parts: [{ part, exercises: [{ name, sets: [{ w, r, note?, drops?: [{w, r}] }], cardio?: {km, min, kcal, note} }] }], createdAt, updatedAt }],
  deletedDayIds: [], exercises: { 部位: [{ name, lastUsedAt }] }, muscleMap: { 種目名: { p: [筋肉id], s: [筋肉id], at, by } } }
```
セット 1 つは `{ w, r }`。v9.6 から **重量だけでも保存する**（`r` は null になりうる。1RM は出ない）。両方空の行はセットとして保存しない。
```
```

**瞑想 `meditation/YYYY.json`**（1 回の瞑想が 1 件。年 = `date` の年、削除の墓標は id の年）
```
{ version: 1, year: 'YYYY', updatedAt,
  sessions: [{ id: 'm_YYYYMMDD_HHMMSS', at: '2026-09-09T21:30:12+09:00'（端末の時刻。時刻帯の集計はこの文字列の時刻で見る）, date: 'YYYY-MM-DD',
               min: 分数, focus: 1〜10 の集中, memo: '', mode: 'timer'|'alarm'|'manual', plannedMin?（アラームの予定分数）,
               noteId?: 言葉にしたときのノートid, createdAt, updatedAt }],
  deletedIds: [{id, deletedAt}] }
```
**索引 `meditation/index.json`**: `{ version: 1, updatedAt, years: { 'YYYY': { updatedAt, count } } }`
1 年 ≈ 550 件・100 KB。27 年分でも端末メモリ 3 MB 程度。連続日数・直近 30 日・月ごとの推移（平均分数・平均集中・中心の時刻±ばらつき）・時間帯・分数ごとの集中は、すべてこの `at / min / focus` から画面で計算する（`medStreak`, `medMonthRows`, `medClock`, `medBandRows`, `medLenRows`）。

### 3.2 同期のしくみ

- 何かを変えると 0.8 秒後に同期。起動時・画面に戻ったとき・オンラインに戻ったときも同期。
- GitHub の Contents API をトークンで直接呼ぶ。読むときは `object` 形式で sha（版の印）を取り、1 MB を超えるファイルは `raw` 形式で本文を取る。書くときは sha 付きで送り、409（別の端末が先に書いた）なら取り直してマージしてもう一度。
- 全部の呼び出しは 30 秒でタイムアウト（`ghFetch`）。
- **言葉（月ファイル）**: `notes/index.json` を読む → 対象の月（端末で変えた月・他端末が変えた月・端末に無い月）を 1 つずつ読む → `mergeNoteSets`（id ごとに `updatedAt` の新しい方。削除は墓標の時刻と比べる）→ 変わっていれば書く → 索引を書く。端末側は保存のたびに月ごとの JSON を前回と比べ、変わった月だけ IndexedDB に書いて「未同期」にする。起動時は `notes:` で始まる全キーを 1 回のカーソル読みで取り込む。
- **記録（月ファイル）**: `journal/index.json` を読む → 今月・先月・端末で変えた月・他端末が変えた月を読む → `mergeJournalSets` → 書く → 索引を書く。端末のメモリには今月・先月と、記録タブや詳細で開いた月だけを載せる。
- **data.json**: ゴミ箱・下書き・使用量・方式フラグ。`mergeData`。
- **筋トレ**: 日ごとに `updatedAt` 新しい方＋墓標。種目カタログと筋肉対応は和集合。
- **瞑想（年ファイル）**: 言葉の月ファイルと同じ作り。`meditation/index.json` を読む → 端末で変えた年・他端末が変えた年・端末に無い年を読む → `mergeMedSets`（1 回ごとに `updatedAt` の新しい方＋墓標）→ 変わっていれば書く → 索引を書く。
- **散歩**: walk10000 と同じ「歩いた日数が多い方が勝つ」（ファイル単位）。
- **引くの順番（v8.2）**: 引くたびに端末のカウンタ（`kotoba_drawExploreN`）が 1 増える。6 の倍数の回は「眠っている言葉」（最後に見た日が古い方から 10%、最低 10 枚、★の有無は問わない）から。それ以外で 3 の倍数の回は「今月」モードで未★の言葉から。残りは重み付き（「今月」）か一様ランダム（「全部」）。相談の候補選びに「残したい」と眠りは入れない。朝の候補にだけ、眠っている言葉を 5 枚足す（選ぶのは AI）。
- 同期バーの文言は `renderSyncBar`。エラーは localStorage の `kotoba_lastSyncError` などに残り、設定の「最終同期エラー」に出る。

### 3.3 AI（Claude API）の使い方

- API キーは端末の localStorage にだけ置く（`kotoba_claudeApiKey`）。data.json には入れない。
- 機能ごとに呼び分け: 朝の言葉・相談（`callChatApi`）、自動関連づけ（`callClaudeApi`、Haiku）、一括入力（`callBulkDecomposeApi`）、問い（`callQuestionApi`：v8.4 から2回呼ぶ。1回目は材料から「種と場面」、2回目は場面と a/b だけから問い `callQuestionAskApi`。材料は2回目に渡さない）、筋肉対応（`generateMuscleMaps`）、読書メモ（`callReadingDecomposeApi`）。
- **撮るはアプリから AI を呼ばない**（v9.0）。カード・答えを壊す・展開・入りの候補は、撮る画面で「プロンプトをコピー」→ Claude のチャットに貼る → 返ってきた JSON をアプリに貼り戻す、という形。1 本の生成に 3 分かかって時間切れになり課金だけ残ったのが理由。週 2 回しか使わないので、チャットの方が確実で安い。
- 貼り戻しの検査はアプリ側にある。JSON として読めなければ入れない。URL は http/https 以外を空にする。枠は `stance`（support / break）から決め、モデルには枠を決めさせない。
- 検索料の算入（`WEB_SEARCH_USD`）はそのまま残してある。撮るからは呼ばなくなったが、他の機能が web 検索を使い始めたときに月上限へ乗る。
- 読書メモは「口述」と「本文の書き写し」のどちらでも受ける。書き写しなら AI が引く価値のある箇所を 1〜3 か所（各 200 字まで）選び、残りを周辺のメモにする。応答はコードフェンスや文字列内の改行があっても読めるように直してから JSON 解析する（`parseReadingReply`）。
- 相談・関連づけに渡す言葉: 言葉が上限（既定 200 枚、設定で変更）以下なら全件を渡してキャッシュ。超えたら「入力に近い言葉」を端末で選んで渡す（`selectCandidateNotes`）。
- 使用量は機能別に月ごと集計し、設定の月上限（USD）を超えると自動関連づけと朝の言葉が止まる。

---

## 4. 直すときの手がかり

### 4.1 主要な定数（index.html を文字列検索）

| 何 | 検索する文字列 |
|---|---|
| リポジトリ名・ファイル名 | `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_PATH`, `TRAINING_PATH`, `JOURNAL_INDEX_PATH`, `NOTES_INDEX_PATH` |
| GitHub の待ち時間 | `GH_TIMEOUT_MS`（30 秒） |
| 候補の言葉の上限・選び方 | `DEFAULT_COMPRESS_THRESHOLD`（200）, `selectCandidateNotes`（本文＋自分の言葉の 2-gram 一致）, `COMPACT_MYWORDS_CHARS`（AI に渡す「自分の言葉」の文字数、120） |
| 種類（名言/本/自分） | `NOTE_KINDS`, `inferNoteKind` |
| 刺さった★の重み（減衰・飽和・休み・探索） | `HIT_TUNING` |
| 「残したい」の効き（倍率 1 + boost ÷ (1 + ★累計)） | `KEEP_TUNING`（boost 0.5）, `keepMultiplier` |
| 眠っている言葉の枠（引くの何回に 1 回・古い方の何割・朝の候補に何枚） | `SLEEP_TUNING`, `sleepingPool`, `lastSeenMap`（「最後に見た日」＝朝・相談・引くで届いた日、問いの材料になった日、眠り順から詳細を開いた日） |
| 問いの角度・プロンプト | `QUESTION_MODES`, `buildQuestionSystemBlocks`（1回目：種 a/b と場面、芯）, `buildQuestionAskSystemBlocks`（2回目：場面だけから問い。(A)建前と本音／(B)二択 の型、責めない、例文）, `ASK_BANNED`（詰問の語。出たら1回書き直させる）, `SCENE_BANNED`（場面・a/b に残った内面の語。出たら1回目を1回書き直させる）。引く結果と日付詳細の「種 ・ a／b　型」で、どちらの工程が外れたかを見る |
| 相談・朝のプロンプト | `buildChatSystemBlocks` |
| 自動関連づけのプロンプト | `buildAutoLinkSystemBlocks` |
| 読書メモのプロンプト | `buildReadingSystemBlocks` |
| 筋肉対応のプロンプト | `buildMuscleSystemBlocks` |
| モデル名の既定値 | `DEFAULT_AUTOLINK_MODEL`, `DEFAULT_CHAT_MODEL` |
| API の max_tokens | 各 `fetch('https://api.anthropic.com` の `max_tokens` |
| 相談・朝の失敗の文言とタイムアウト | `chatErrorText`（種類ごとの文）, `CHAT_TIMEOUT_MS`（60 秒）。失敗の詳細（ステータス・応答の冒頭 200 字・モデル名）は設定の「最終エラー」に入る |
| 筋トレの桁の警告 | `TR_OUTLIER_RATIO`（前回までの最大の 1.5 倍を超えたら警告）, `TR_MAX_PLAUSIBLE_REPS`（60 回）。止めずに警告だけ出す |
| 使用量の単価 | `MODEL_PRICING` |
| 端末保存のキー | `KV_DB_NAME`, `STORAGE_KEY`, `BACKUP_MAX_CHARS` |
| 筋トレ画像のデザイン | `trLayout`, `trDrawPage`（`TR_GREEN` など） |
| 3D の色・モデル URL | `MUSCLE_COLORS`, `MUSCLE_BIN_URL`, `THREE_MODULE_URL` |
| 筋肉一覧 | `MUSCLE_CATALOG`（`assets/muscles.json` と同じ） |
| 網の見た目 | `GRAPH_FIT_FLOOR`, `graphPathsFrom` |
| 画面のスクロール構造 | `#shell`（v7.3。この箱がスクロールし、ページ自体は動かない） |
| 瞑想 | `MEDITATION_INDEX_PATH`, `MED_MIN_PRESETS`（5/10/15/20）, `MED_BELLS`（鈴の倍音。試聴ページと同じ計算）, `MED_BELL_DEFAULT`, `MED_BELL_KEY`（選んだ音）, `MED_TIMER_KEY`（計測中の開始時刻）, `MED_ALARM_CUSTOM_KEY`（任意分数の前回値）。時間帯の区切りは `medBandOf`（朝 5〜11 / 昼 11〜17 / 夜） |
| 撮るのプロンプトと取り込み（v9.0。アプリは AI を呼ばない） | `shootCardsPromptText` / `shootBreakPromptText` / `shootFlowPromptText` / `shootHookPromptText`（チャットに貼る完成形）, `shootImportCards` / `shootImportBreak` / `shootImportFlow` / `shootImportHooks`（貼り戻した JSON の取り込み）, `shootParseJson`, `cardsFromItems`（枠は `stance` から決め、URL は `shootSafeUrl` を通す） |
| 検索料 | `WEB_SEARCH_USD`（1 回 $0.01）。`recordApiUsage` が `usage.server_tool_use.web_search_requests` を `searches` として貯め、`estimateCostUsd` が金額に足す。**これが無いと月上限に検索料が乗らない** |
| 撮るの答えの履歴 | `SHOOT_HISTORY_GAP_MS`（仮の答えの履歴をまとめる間隔） |
| 撮る（話の型の枠） | `TALK_SLOTS`（枠の定義。ここだけ直せば名前・並び・受け入れる種類が変わる）, `defaultSlotFor`（新しいカードがどの枠に入るか。判断はコード側、モデルは `stance` を返すだけ） |
| 撮る（デッキの中の相談） | `shootConsultSeed`（相談に投げる文の初期値＝問い＋仮の答え）, `shootConsultAsk`（相談タブと同じ `callChatApi`。★も同じ hit として記録される）。選んだ札はその場で「言葉」の枠のカードになる |
| 流れの説明 | `shootNotePromptText`（縛りはここ）, `deck.flowNote`, `shootStageIntro`（撮影表示を開いたとき先に出る全画面） |
| 撮る編集画面の進み方 | `updateShootAddButtons`（名前は古いが全ブロックの可否を決める）, `shootGate`（薄くする＋理由の 1 行） |
| 撮影表示（カンペ） | `shootCardLabel`（label、無ければ本文の先頭 15 字）, `shootSourceShort`（出典の略、18 字）, `renderShootStageCards`（1 行表示・タップで 1 枚だけ展開・長押し 0.5 秒で薄く） |
| 撮る（デッキ・カード・撮影表示） | `SHOOT_SAVE_MS`（自動保存 0.4 秒）, `SHOOT_CARD_LABEL`, `SHOOT_BELIEF_LABEL`, `SHOOT_USED_PICK_DAYS`（「使う」印を拾う日数、30）, `shootSafeUrl`（出典を開くのは http/https だけ）, `normalizeDeckCard` |
| 振り返る（記録タブの入り口） | `LOOKBACK_SEARCH_DAYS`（記録のない日から近い日を探す範囲、400 日）, `DAY_NOTES_SHOWN`（その日に追加した言葉の表示枚数、5）, `dayPositionLine`（「一万日の N 日目 / 10000 ・ 言葉 ・ 筋トレ ・ 瞑想」の行）, `dayHeadlineNote`（その日の言葉：★ → 朝の最初の言葉） |
| 入力の退避（未保存の下書き） | `INPUT_DRAFT_KEY`, `captureInputDraftNow`, `restoreInputDraft`（対象外にしたい欄は `INPUT_DRAFT_SKIP`、画面ごと外すのは `INPUT_DRAFT_SKIP_SCREENS`）, `INPUT_DRAFT_NAV_MAX_AGE_MS`（これより古い下書きは起動時にその画面へ飛ばない。開いたときに入るだけ） |

### 4.2 直して反映するまで

1. `index.html` を編集する（1 ファイルだけ）。
2. 文法チェック（PC に Node.js があれば）:
   ```
   node -e "const s=require('fs').readFileSync('index.html','utf8');const a=s.indexOf('<script>\n(async () => {');const b=s.lastIndexOf('</script>');require('fs').writeFileSync('app.js',s.slice(a+8,b))" && node --check app.js
   ```
   何も表示されなければ OK。エラーが出たら行番号を見て直す。
3. ローカルで見る: `npx http-server -p 8731` で `http://localhost:8731/`。
4. `git add index.html && git commit -m "説明" && git push`。1 分ほどで反映。
5. 壊したら 2.5 で前のコミットに戻す。

### 4.3 本番のデータを触らずに試す（偽 GitHub のテスト版）

`index.html` のコピーを `_test_index.html` として作り、`<script>\n(async () => {` の直前に `fetch` を差し替えるスクリプトを挟む（`api.github.com/repos/…/contents/…` への GET/PUT をメモリ上の `{sha, text}` で応える。PUT は sha が違えば 409）。localStorage の `kotoba_ghToken` に何か入れれば同期が走る。`_` で始まるファイルは `.gitignore` でコミットされない。

---

## 5. ライセンス表記

- 3D モデル: BodyParts3D, © The Database Center for Life Science, CC BY 4.0（広背筋・腹直筋は皮膚表面からの近似）。
- フォント: DotGothic16（Google Fonts）。
- three.js（MIT、jsdelivr から読み込み）。

---

## 6. 次の壁（時期の目安と、そのとき何をするか）

| 壁 | 目安 | 何が起きるか | 対策 |
|---|---|---|---|
| 言葉が 3 万枚（27 年）を超える | 1 日 3 枚のペースで 27 年 | ファイル分割は月ごとなので問題なし（324 ファイル・約 105 MB）。壁は端末側：起動時に全件を読むので iPhone で 3〜5 秒、メモリ 150〜250 MB。10 万枚（1 日 10 枚）だと起動 10 秒超 | そのときは「古い月を起動時に読まない」改修（`notesBoot` で読む月を絞り、記録タブや詳細で必要になったら読む。記録の月ファイルと同じ作り） |
| 候補の言葉の上限（既定 200 枚） | 2027 年初め | 200 枚を超えると相談・自動関連づけは「入力に近い言葉」だけを渡す。1 回あたりのトークンが全件キャッシュ時の約 3 倍（Sonnet で $0.03/相談） | そのまま使える。物足りなければ `selectCandidateNotes` のスコア（2-gram 重なり・タグ・種類・★の重み・新しさ）を調整 |
| API の月上限（既定 $2） | 読書メモを使い始めたら | 読書メモ 1 回 ≈ $0.01〜0.015。1 日 10 回で **月 $4〜5** | 設定 → Claude API → 月の上限を $10 程度に上げる |
| 瞑想の記録が 27 年分（約 1.5 万件） | 2053 年 | 年ファイルなので 1 ファイル 100 KB 前後のまま。端末メモリ 3 MB 程度 | 何もしなくてよい |
| トークンの期限（最長 1 年） | 作った日から 1 年 | 同期が 401 で止まる | 2.1 で作り直す |
