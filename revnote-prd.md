# Revnote - プロダクト要件定義書（PRD）

> 反映バージョン: v5.5。実装の詳細は CLAUDE.md を参照。

---

## 1. プロダクト概要

**中学受験の「リベンジノート」をデジタル化し、忘却曲線で復習タイミングを最適化するアプリ**

- **対象**: 小学4〜6年、偏差値50帯、塾なし〜中小塾
- **価値**: 間違えた問題を登録 → 最適タイミングで復習 → 定着。保護者は「分析」タブで進捗・弱点を把握。
- **コンテンツ**: 持たない。塾テキスト・市販教材を撮影して登録するプロセス管理ツール。

---

## 2. 技術構成（現行）

| 項目 | 内容 |
|------|------|
| フロント | 単一HTML（Vanilla JS, CSS）。iPad + Apple Pencil 想定 |
| ホスティング | GitHub Pages（ppxa.github.io/revnote/） |
| データ | localStorage。オプションで Supabase 同期 |
| デプロイ | `revenge-note.html` → `index.html` にコピー後 `git push origin master:main` |

---

## 3. 機能一覧（v5.5 時点）

| 領域 | 機能 | 状態 |
|------|------|------|
| 復習 | SM-2 ベース忘却曲線、dailyCap、教科/タイプフィルタ | ✅ |
| 登録 | 教科・単元・写真/テキスト・答え・ヒント・間違い理由・出典 | ✅ |
| 復習UI | スクラッチパッド、◎△×、メモ蓄積、タイマー | ✅ |
| デッキ | 初回用プリセット12デッキ、設定で追加/削除 | ✅ |
| 履歴 | カレンダー、今日デフォルト、詳細モーダル | ✅ |
| 分析 | ストレッチゾーン、教科別定着率、弱点・週間サマリー等 | ✅ |
| ゲーム | XP/レベル/称号/ストリーク/ボス戦、ご褒美ミニゲーム | ✅ |
| アバター | SVGパーツ、XPでアクセサリー購入 | ✅ |
| 塾連動 | 四谷/SAPIX/日能研進度、習っていない問題フィルタ | ✅ |

**設計上の廃止事項**: 親子モード切替UI（保護者機能は分析タブに統合）、AI機能（v4.3 で削除）、ランプ表示（ゲージに統一）。

---

## 4. データ構造の要点

- **DATA.problems[]**: id, subject, topic, source, content/contentImage, answer/answerImage, hint, deckId, 正誤履歴(history), 描画・メモ、curriculum、nextReviewDate 等。
- **DATA.settings**: dailyCap, birthDate, jukuType, examDate, examName 等。
- **DATA**: streak, sessionLog, xp, avatar。

詳細は CLAUDE.md の「データ構造 (localStorage)」を参照。

---

## 5. 今後の検討（ロードマップ）

- 週間・月間レポート、優先復習の自動提案
- 共有・PDF出力、NOTE 連携・マネタイズ
- バックエンド or JSON ベースの親子共有

優先度とフェーズは revnote-roadmap.md を参照。

---

## 6. 参照

- 開発時: **README.md** → **CLAUDE.md** → 本ファイル（必要時）
- 変更履歴: **CHANGELOG.md**
