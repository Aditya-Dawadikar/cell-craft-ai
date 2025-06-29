import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { SessionState } from "../interfaces/SessionInterface";

const initialState: SessionState = {
    sessions: [],
    activeSession: null
}

const sessionSlice = createSlice({
    name: 'user_sessions',
    initialState,
    reducers: {
        addSession: (state, action: PayloadAction<any>) => {
            state.sessions.push(action.payload)
        },
        deleteSession: (state, action: PayloadAction<any>) => {
            state.sessions = state.sessions.filter((elem, idx) => {
                elem.session_id != action.payload
            })
        },
        loadSessions: (state, action: PayloadAction<any>) => {
            state.sessions = action.payload
        },
        setActiveSession: (state, action: PayloadAction<any>) => {
            state.activeSession = action.payload
        }
    }
})

export const { loadSessions, addSession, setActiveSession } = sessionSlice.actions
export default sessionSlice.reducer