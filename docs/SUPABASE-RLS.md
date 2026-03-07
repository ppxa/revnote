# Supabase RLS 確認手順

Revnote は Supabase の `user_data` テーブルにログインユーザーごとのデータを保存します。anon key はソースに含まれており公開前提です。**他ユーザーのデータを読めないようにするため、RLS（Row Level Security）の設定が必須です。**

## 確認手順

1. **Supabase ダッシュボード**にログインする。  
   プロジェクト: `hciwivjeuqgywwjdeegn`（CLAUDE.md の SUPABASE_URL に含まれる ref）

2. **Table Editor** で `user_data` テーブルを開く。

3. **RLS が有効か確認**
   - 左サイドバー **Authentication** → **Policies**、または **Table Editor** で `user_data` を選択
   - 「RLS enabled」が **ON** になっていること

4. **ポリシーが存在するか確認**
   - `user_data` に対して次のポリシーがあること（または同等の制限）:
     - **SELECT**: `auth.uid() = user_id`（自分の行だけ読める）
     - **INSERT**: `auth.uid() = user_id`（自分の user_id でだけ挿入できる）
     - **UPDATE**: `auth.uid() = user_id`（自分の行だけ更新できる）
     - **DELETE**: `auth.uid() = user_id`（自分の行だけ削除できる）

## 未設定の場合の追加方法

- **Policies** 画面で **New Policy** を選択
- テンプレート「Enable read access for users based on user_id」等を選ぶか、手動で:
  - Policy name: 例 `user_data_own_only`
  - Allowed operation: 必要なもの（SELECT, INSERT, UPDATE, DELETE）
  - Target roles: `authenticated` または `anon`（anon でログインしている場合は anon）
  - USING expression: `auth.uid() = user_id`
  - WITH CHECK expression（INSERT/UPDATE 用）: `auth.uid() = user_id`

## 確認の簡易テスト

- ブラウザで Revnote を開き、別のアカウントでログインしてデータを保存
- 別のアカウントでログインし直し、先のアカウントのデータが表示されないこと・自分のデータだけ表示されることを確認
