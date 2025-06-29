export interface Session{
    session_id: string
    session_name: string
}

export interface SessionList{
    sessions: Session[]
}

export interface SessionState{
    sessions: Session[],
    activeSession: Session | null
}