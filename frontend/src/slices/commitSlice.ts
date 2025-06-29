import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { CommitHistoryState } from "../interfaces/CommitInterfance";


const initialState: CommitHistoryState = {
    head: null,
    commits: [],
    selectedCommit: null
}

const commitSlice = createSlice({
  name: 'commit_history',
    initialState,
    reducers: {
        addCommit: (state, action: PayloadAction<any>)=>{

        },
        removeCommit: (state, action: PayloadAction<any>)=>{

        },
        setHead: (state, action: PayloadAction<any>)=>{

        },
        setSelectedCommit: (state, action: PayloadAction<any>)=>{
            state.selectedCommit = action.payload.selectedCommit
        },
        setCommitHistory: (state, action: PayloadAction<any>)=>{
            state.head = action.payload.head
            state.commits = action.payload.commits
            state.selectedCommit = action.payload.head
        }
    }
})

export const {addCommit, removeCommit, setHead, setCommitHistory, setSelectedCommit} = commitSlice.actions
export default commitSlice.reducer
