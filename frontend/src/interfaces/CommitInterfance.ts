export interface Commit{
    commit_id: string,
    parent_id: string | null,
    timestamp: string
}

export interface CommitHistoryState {
    head: Commit | null,
    commits: Commit[]
}
