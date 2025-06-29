import type { Commit } from "./CommitInterfance"

export interface ChatMessage {
    text: string,
    sender: 'user' | 'bot',
    code?: string,
    key_steps?: string,
    df_head?: JSON,
    generated_files?: [string],
    commit_data?: Commit,
    error?: string,
    mode?: string,
    action?: string,
    message?: string,
    new_head?: string
}

export interface ChatState {
    session_id: string,
    messages: ChatMessage[]
}
