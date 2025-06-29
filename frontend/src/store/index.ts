import { configureStore } from "@reduxjs/toolkit";
import chatReducer from '../slices/chatSlice'
import CommitReducer from '../slices/commitSlice'

export const store = configureStore({
    reducer:{
        chat: chatReducer,
        commit: CommitReducer
    },
    devTools: import.meta.env.NODE_ENV !== 'production', 
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch