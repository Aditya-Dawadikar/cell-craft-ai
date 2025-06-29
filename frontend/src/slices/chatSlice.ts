import {createSlice} from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { ChatMessage, ChatState } from '../interfaces/ChatMessageInterface'


const initialState: ChatState = {
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
        }
    }
})

export const {addMessage, clearMessages} = chatSlice.actions
export default chatSlice.reducer