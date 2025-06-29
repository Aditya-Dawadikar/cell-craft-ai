import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { CommitHistoryState } from "../interfaces/CommitInterfance";


const initialState: CommitHistoryState = {
    head: null,
    commits: []
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
        setCommitHistory: (state, action: PayloadAction<any>)=>{
            state.head = action.payload.head
            state.commits = action.payload.commits
        }
    }
})

export const {addCommit, removeCommit, setHead, setCommitHistory} = commitSlice.actions
export default commitSlice.reducer
