import { configureStore } from "@reduxjs/toolkit";
import chatReducer from '../slices/chatSlice'
import CommitReducer from '../slices/commitSlice'
import SessionReducer from '../slices/sessionSlice'

export const store = configureStore({
    reducer:{
        chat: chatReducer,
        commit: CommitReducer,
        session: SessionReducer
    },
    devTools: import.meta.env.NODE_ENV !== 'production', 
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch