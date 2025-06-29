import {createSlice} from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { ChatMessage, ChatState } from '../interfaces/ChatMessageInterface'


const initialState: ChatState = {
    session_id: 'e73358fc-2da7-44d5-8d05-7a5d85b124f2',
    messages: []
}

const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        addMessage: (state, action: PayloadAction<ChatMessage>) => {
            state.messages.push(action.payload)
        },
        clearMessages: (state) => {
            state.messages = []
        },
        setSession: (state, action: PayloadAction<any>)=>{
            state.session_id = action.payload.session_id
        }
    }
})

export const {addMessage, clearMessages} = chatSlice.actions
export default chatSlice.reducer