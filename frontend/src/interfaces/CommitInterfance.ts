export interface Commit{
    commit_id: string,
    parent_id: string | null,
    timestamp: string,
    key_steps: string
}

export interface CommitHistoryState {
    head: Commit | null,
    commits: Commit[],
    selectedCommit: Commit | null
}
