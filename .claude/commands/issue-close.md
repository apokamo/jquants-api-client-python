---
description: イシュー完了時に使用。PRマージ・worktree削除・ブランチ削除を一括実行
---

# Issue Close

イシュー対応完了後のクリーンアップを実行します。

## いつ使うか

| タイミング | このスキルを使用 |
|-----------|-----------------|
| PRがApproveされマージ可能 | ✅ 使用 |
| PRレビュー待ち | ❌ 待機 |
| 作業途中 | ❌ 不要 |

## 引数

```
$ARGUMENTS = <issue-number> [prefix]
```

- `issue-number` (必須): Issue番号 (例: 8)
- `prefix` (任意): ブランチプレフィックス (デフォルト: feat)

## 前提条件

- Merge commit方式を使用（ブランチ履歴を保持）
- マージコメントの追加入力は不要

## 実行手順

### Step 0: 引数の解析

$ARGUMENTS から issue-number と prefix を取得してください。
- prefix が指定されていない場合は `feat` をデフォルトとする
- ブランチ名: `[prefix]/[issue-number]`
- ディレクトリ: `../jquants-[prefix]-[issue-number]`

### Step 1: PRのマージ

```bash
gh pr merge --merge --delete-branch
```

マージコミットを作成してブランチ履歴を保持する。

### Step 2: venv シンボリックリンク削除

worktree 削除前に `.venv` シンボリックリンクを削除（untracked files エラー回避）:

```bash
rm ../jquants-[prefix]-[issue-number]/.venv
```

### Step 3: メインリポジトリに移動してworktree削除

```bash
cd /home/aki/claude/jquants-api-client-python
git worktree remove ../jquants-[prefix]-[issue-number]
```

### Step 4: 完了報告

以下の形式で報告してください:

```
## Issue クローズ完了

| 項目 | 状態 |
|------|------|
| PR | マージ済み |
| worktree | 削除済み |
| リモートブランチ | 削除済み (--delete-branch) |

作業ディレクトリは /home/aki/claude/jquants-api-client-python に戻りました。
```
