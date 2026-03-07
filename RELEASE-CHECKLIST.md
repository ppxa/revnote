# リリース前チェックリスト（批判的）＆ スケジュール

> 目標: **明日夜まで**にリリース可能な状態にする。今日〜明日夜を「自由に使える」前提。

---

## 1. 批判的に指摘する「必須で直すべき点」

### 1-1. リポジトリの汚れ（リリースの顔）

| 問題 | 批判 | 対応 |
|------|------|------|
| **ルートに環境用ファイルが混入** | `.config`, `.local`, `.npm`, `.npm-global`, `.wget-hsts` がリポジトリに入っている。第三者・AI が「本番用リポジトリ」と信頼しづらい。 | これらを `.gitignore` に追加し、`git rm -r --cached` で追跡だけ外す。必要ならローカルでは削除。 |
| **README が無い** | GitHub のトップが「中学受験リベンジノート」の1行だけ。何のアプリか・どう動かすか・ドキュメントがどこか分からない。 | `backup-before-clone/README.md` をルートに復元するか、同内容で `README.md` を新規作成。 |
| **古い PRD が残っている** | `StudyFlow-PRD.md` / `studyflow-prd.md` が残っている（大文字小文字で1本だけ見えている可能性あり）。名前が Revnote に統一済みなのに「StudyFlow」が残ると混乱する。 | 両方削除。`revnote-prd.md` が正式 PRD であることを README か CLAUDE に明記。 |

### 1-2. アプリの堅牢性（初回・インポートで落ちないように）

| 問題 | 批判 | 対応 |
|------|------|------|
| **defaultData() が不足している** | `defaultData()` が `version, problems, settings{dailyCap, freezeThreshold}, streak, sessionLog` しか返さない。コードは `DATA.xp`, `DATA.avatar`, `DATA.settings.examDate`, `birthDate`, `jukuType`, `examName`, `schoolLevel`, `mode` を参照している。初回起動や古いエクスポートのインポートで undefined 参照になりうる。 | `defaultData()` に `xp: 0`, `avatar: getDefaultAvatar() 相当の初期値`, `settings` に `examDate, birthDate, jukuType, examName, schoolLevel, mode` を追加する。 |
| **インポートで上書きしすぎ** | `importData` が `DATA = imported` で丸ごと差し替えている。インポート JSON に `settings` や `xp` が無いと、既存の設定が消え、その後の参照で undefined になる可能性がある。 | インポート時に `defaultData()` とマージする。例: `DATA = Object.assign({}, defaultData(), imported);` のあと `DATA.problems = imported.problems || [];` など、problems は必ずインポート側を採用。 |
| **インポートのエラーハンドリング** | `JSON.parse` は try/catch 済み。ただし「不正な JSON」以外（例: problems が配列でない）で落ちる可能性はある。 | 時間があれば `imported.problems` が配列か検証し、なければ alert して return。必須ではないがやると安心。 |

### 1-3. デプロイ・公開

| 問題 | 批判 | 対応 |
|------|------|------|
| **index.html と revenge-note.html の不一致** | 開発は `revenge-note.html`、GitHub Pages は `index.html` を読む。push 前に `cp revenge-note.html index.html` を忘れると、公開されているのが古いままになる。 | リリース前に必ず `cp revenge-note.html index.html` を実行し、両方コミットしてから push。 |
| **Supabase の anon key がソースに直書き** | これは Supabase の想定用法（anon key は公開前提）。ただし **RLS（Row Level Security）** が有効で、`user_data` が「自分の user_id だけ」に限定されているか未確認だと危険。 | 本番で Supabase を使うなら、ダッシュボードで `user_data` の RLS を確認。「user_id = auth.uid()」で読書・書込が制限されていること。 |

### 1-4. ドキュメントの一致

| 問題 | 批判 | 対応 |
|------|------|------|
| **ロードマップが v4 のまま** | `revnote-roadmap.md` が「v4.0 ロードマップ」「親子モード」と書かれたまま。v5.3 で親子切り替えは廃止済み。 | 前回整理した `backup-before-clone/revnote-roadmap.md`（v5.5 反映・親子モード廃止注記）で上書きする。 |
| **CLAUDE.md のファイル一覧が古い** | `StudyFlow-PRD.md` と書いてある。 | `revnote-prd.md` に修正。 |

---

## 2. やると良いが「必須でない」もの

- **エクスポートファイル名**: 現在 `revenge-note-${today()}.json` → `revnote-${today()}.json` にすると名前統一。優先度は低い。
- **初回オンボーディング**: 「サンプルデータを読み込む」を最初に案内する画面は無くてもリリース可。後続で追加可能。
- **親子モードの残骸**: `applyMode()`, `DATA.settings.mode` が残っていても、UI で切り替えできなければ実害は小さい。時間がなければ触らなくてよい。

---

## 3. 明日夜までのスケジュール案

### 今日（残り時間）

| 時間 | やること | 成果物 |
|------|----------|--------|
| 30分 | リポジトリ掃除 | `.gitignore` に `.config`, `.local`, `.npm`, `.npm-global`, `.wget-hsts` を追加。`git rm -r --cached .config .local .npm .npm-global`（存在するものだけ）。StudyFlow-PRD.md / studyflow-prd.md を削除。 |
| 15分 | README 追加 | `backup-before-clone/README.md` をルートにコピーして `README.md` として保存（または既存の整理版を採用）。 |
| 30分 | defaultData と importData の修正 | `defaultData()` に xp, avatar 初期値、settings の不足フィールドを追加。`importData` で defaultData とマージしてから problems をインポート側で上書き。 |
| 15分 | ドキュメント更新 | `revnote-roadmap.md` を backup 版（v5.5 反映）で上書き。`CLAUDE.md` のファイル構成を revnote-prd.md に修正。 |

### 明日 午前

| 時間 | やること | 成果物 |
|------|----------|--------|
| 45分 | 動作確認（必須パス） | 1) 初回起動（データ無し）でクラッシュしない 2) 問題1問登録 → 復習 → ◎/△/× 3) エクスポート → 別ブラウザ or シークレットでインポート 4) 設定で生年月日・入試日を入れてカウントダウン表示 5) サンプルデータ読み込み → 今日のキューが出る。 |
| 15分 | index 同期とコミット | `cp revenge-note.html index.html`。CHANGELOG に「v5.5.1 リリース準備: defaultData/import 強化、README 追加、リポジトリ掃除」など1行追記。commit & push（main に直接 or ブランチで PR）。 |

### 明日 午後

| 時間 | やること | 成果物 |
|------|----------|--------|
| 20分 | Supabase 確認 | Supabase ダッシュボードで `user_data` の RLS を確認。未設定なら「user_id = auth.uid()」でポリシー追加。 |
| 30分 | 軽い UI 確認 | iPad または DevTools のモバイル表示で、今日・登録・一覧・履歴・分析・設定を一通り開き、明らかなレイアウト崩れがないか確認。 |
| 20分 | デプロイと本番確認 | `git push origin master:main`（または main への push）で GitHub Pages を更新。https://ppxa.github.io/revnote/ で開き直し、上記の必須パスを1回ずつ実行。 |

### 明日 夜（締め）

| やること | 成果物 |
|----------|--------|
| 本番 URL で最終チェック | 問題なければリリース完了。 |
| NOTE 用の1行紹介を用意（任意） | 例: 「中学受験のリベンジノートをデジタルで。忘却曲線で復習タイミングを最適化するアプリ Revnote を公開しました。」 |

---

## 4. まとめ

- **必須**: リポジトリ掃除、README、defaultData/importData の強化、index 同期、ドキュメント（roadmap・CLAUDE）の更新、動作確認、Supabase RLS 確認、push & 本番確認。
- **必須ではない**: エクスポートファイル名の変更、オンボーディング追加、親子モード残骸の削除。
- **見積もり**: 今日 約1.5時間 + 明日 午前1時間・午後約1時間・夜の確認で、明日夜までにリリース可能。

このファイルはリリース後に削除しても、`revnote-roadmap.md` や CHANGELOG に「v5.5.1 リリース」を残しておくとよい。
