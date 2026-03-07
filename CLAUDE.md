# Revnote - Claude Code 開発ガイド

## プロジェクト概要

中学受験（小学4〜6年生）向け間違い直しノートアプリ。「リベンジノート」のデジタル版。
偏差値50帯、塾なし〜中小塾の子がターゲット。

**コンセプト**: 間違えた問題を登録 → 忘却曲線(SM-2)で最適タイミングに復習 → 定着

## 技術スタック

- **単一HTMLファイル** (`revenge-note.html` = `index.html`)
- **フレームワークなし**: Vanilla JS, CSS, HTML のみ
- **データ永続化**: localStorage (JSON)
- **ホスティング**: GitHub Pages (`ppxa.github.io/revnote/`)
- **フォント**: Zen Maru Gothic (Google Fonts)
- **クラウド同期**: Supabase (実装済み、オプション)

## リポジトリ

- **GitHub**: `https://github.com/ppxa/revnote.git`
- **ブランチ**: `master` (ローカル) → `main` (GitHub Pages が参照)
- **デプロイ**: `git push origin master:main`
- **注意**: Personal Access Token が必要。セッションごとに設定が必要。

```bash
git remote set-url origin https://x-access-token:TOKEN@github.com/ppxa/revnote.git
git push origin master:main
```

## ファイル構成

```
revenge-note.html   # メインアプリ（全コード）= index.html と同一
index.html          # GitHub Pages 用コピー
.gitignore          # .cache/ 等を除外
revnote-prd.md      # プロダクト要件定義（現行仕様）
revnote-roadmap.md  # ロードマップ
CLAUDE.md           # 本ファイル（開発ガイド）
CHANGELOG.md        # バージョン履歴
curriculum_v2.js    # カリキュラムデータ（塾別）
gen_curriculum_v2.py # カリキュラム生成スクリプト
generate_samples.py  # サンプル問題生成スクリプト
```

## 現在のバージョン: v5.5

### コア機能

1. **忘却曲線 (SM-2ベース)**
   - EaseFactor による動的間隔調整
   - 正解 → 間隔伸びる / 不正解 → リセット / あやしい → 半減
   - ステージ: new → learning → reviewing → mastered

2. **問題登録**
   - 教科（算数/国語/理科/社会）+ 単元（2階層プリセット）
   - テキスト or 写真（カメラ/クリップボード）
   - 答え + 解き方ヒント（1行）
   - 出典、難易度、頻出度、タグ、正答率
   - 間違い理由（計算ミス/読み違い/知識不足/解法不明/ケアレス/時間切れ）

3. **復習セッション**
   - 毎日のキュー生成（dailyCap設定可能、デフォルト15問）
   - 教科・タイプ（思考/暗記）でフィルタ可能
   - 問題表示 → 手書きスクラッチパッド → 答え確認 → ◎△× 自己評価
   - 経過時間の自動計測
   - メモ蓄積（過去のメモがヒントとして表示）

4. **デッキシステム**
   - 初回体験用のプリセット問題（4/5/6年 × 漢字/算数/理科/社会 = 12デッキ）
   - 算数デッキには解き方ヒント付き
   - 設定画面からデッキ別に追加/削除可能
   - `deckId` フィールドで管理

5. **カレンダー/履歴**
   - デフォルトで今日が選択された状態
   - 日付セルに◎△×ドット＋問題数表示
   - タップで詳細モーダル（問題文、答え、ヒント、描画、メモ、間違い理由）

6. **分析（旧ダッシュボード + 保護者機能統合）**
   - ストレッチゾーン（最適負荷の問題分類）
   - 教科別定着率
   - 弱点分析、間違いパターン、繰り返し間違える問題
   - 週間サマリー、優先復習提案、成長記録、学習アドバイス

7. **ゲーミフィケーション**
   - XP システム（正解+15, あやしい+8, 不正解+3, 定着ボーナス+30）
   - レベルシステム: Lv = floor(sqrt(xp/50)) + 1
   - 称号: 見習い→がんばり屋→努力家→チャレンジャー→実力者→達人→マスター→博士→レジェンド→神
   - ストリーク（連続日数）
   - ボス戦（5レベルごと）
   - **ご褒美ミニゲーム**: dailyCap達成後にスロット or コイン落とし
     - スロット: 3リール、3回まで、JACKPOT 100XP
     - コイン落とし: Canvas物理演算、5枚、+5〜+50 XP

8. **アバターシステム**
   - SVGパーツ組み合わせ（肌色/髪型/髪色/目/目色/口/アクセサリー）
   - ヘッダにミニアバター表示（タップで編集）
   - アクセサリーはXPで購入（200〜500 XP）
   - `DATA.avatar` に保存

9. **ヘッダバッジ（3秒ローテーション）**
   - 入試カウントダウン → Lv.X + 称号 → XP合計

10. **塾カリキュラム連動**
    - 四谷大塚/SAPIX/日能研の進度データ内蔵 (`CURRICULUM_V2`)
    - 生年月日から現在の学年・月を自動算出
    - 習っていない問題のフィルタリング

### UI/レイアウト

- **ヘッダ**: アバター + revnote + タイマー（タップで切替）+ ▶↺ + バッジ + 保存
- **ヘッダ直下**: 進捗ゲージ（今日の完了数/目標）+ ラベル（ゲージ下・右寄せ）
- **ボトムナビ**: 今日 / 登録 / 一覧 / 履歴 / 分析 / 設定
- **配色**: コーラル系（--accent: #f0896c）、温かみのあるデザイン
- **iPad横向き**: 左ペイン（問題+操作）+ 右ペイン（計算スペース）

### データ構造 (localStorage)

```javascript
DATA = {
  version: '1.0',
  problems: [{
    id, subject, topic, source, content, contentImage,
    answer, answerImage, hint,  // ← v5.3で追加
    deckId,                      // ← v5.0で追加（デッキ管理用）
    correctRate, frequency, difficulty, tags,
    problemType,  // 'flash' or null (think)
    easeFactor, interval, repetitions, consecutiveFailures,
    masteryLevel, nextReviewDate, frozen,
    history: [{ date, result, quality, memo, mistakeReason, timestamp, timeSpent }],
    memos: [], lastMemo, lastDrawing, lastDrawingImage,
    curriculum: { yotsuya: "4-04", sapix: "4-02", nichinoken: "4-04" },
    createdAt, createdTimestamp
  }],
  settings: {
    dailyCap, freezeThreshold, birthDate, jukuType,
    examDate, examName, schoolLevel, mode
  },
  streak: { count, lastDate, history },
  sessionLog: [{ date, correct, wrong, hard, graduated }],
  xp: 0,
  avatar: { face, hair, hairColor, eyes, eyeColor, mouth, accessory, unlockedAccessories }
}
```

### 重要な設計判断

- **親子切り替えは削除済み**: 保護者機能は「分析」タブに統合
- **一覧のボタン**: 「解く」「編集」のみ。削除・凍結は編集ダイアログ内
- **ランプ（進捗ドット）は削除済み**: ヘッダ直下のゲージに置き換え
- **AI機能は削除済み**: v4.3で全削除。Claude APIは使っていない
- **単一ファイル**: 全HTML/CSS/JSが1ファイル。分割しない
- **フレームワーク禁止**: React, Vue等は使わない。Vanilla JSのみ

### 開発パターン

- 変更は `revenge-note.html` に行う
- デプロイ前に `cp revenge-note.html index.html` を忘れずに
- `.cache/` がgitに入ると100MB制限で弾かれる → `.gitignore` に入っている
- `git push origin master:main` でデプロイ（masterブランチはローカル、mainがPages用）

### 今後の方向性

- アプリ名変更検討中（StudyFlow → ReFlow → ?）
- NOTE記事によるマネタイズ・需要検証
- バックエンド or JSON-based persistence（parent-child共有用）
- GitHub Organization の整理（ppxa）
- カリキュラム進度フィルタリングの強化
