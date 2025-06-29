import { Box, Button, Collapse, Paper, Stack } from '@mui/material'
import CommitHistory from './DataTiles/CommitHistory'
import { useState } from 'react'
import PanelGrid from './DataTiles/PanelGrid'
import { Tooltip } from '@mui/material'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState } from '../store/index'
import { Autocomplete, Typography, TextField } from '@mui/material'
import { getCommitFiles } from '../services/commit'
import { setSelectedCommit } from '../slices/commitSlice'

type Panel =
    | { type: 'dataframe'; title: string; url: string }
    | { type: 'readme'; title: string; url: string }
    | { type: 'chart'; title: string; url: string }

const DataPreview = () => {

    const dispatch = useDispatch()

    const [drawerOpen, setDrawerOpen] = useState(false)

    const commitList = useSelector((state: RootState) => state.commit.commits) ?? []
    const commitHead = useSelector((state: RootState) => state.commit.head)
    const selectedCommit = useSelector((state: RootState) => state.commit.selectedCommit)
    const sessionIdFromStore = useSelector((state: RootState) => state.chat.session_id)

    const [panels, setPanels] = useState<Panel[]>([])


    const truncate = (str: string | undefined | null, len = 50) =>
        str && str.length > len ? str.slice(0, len) + '...' : str ?? ''

    const handleFetchFiles = async (commit_id: string) => {
        const data = await getCommitFiles(sessionIdFromStore, commit_id)

        console.log("commit files", data)

        setPanels([...data.files])
    }

    const handleSelectCommit = (commit_id: string) => {
        console.log(commit_id)
        dispatch(setSelectedCommit(commit_id))
        handleFetchFiles(commit_id)
    }

    return (
        <Paper
            elevation={2}
            sx={{
                height: 'calc(100vh - 32px)',
                m: 1,
                p: 1,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
            }}
        >
            <Stack direction="row" spacing={2} mb={2}>
                <Button variant="contained" onClick={() => setDrawerOpen((prev) => !prev)}>
                    {drawerOpen ? 'Hide' : 'Show'} Commit History
                </Button>

                <Autocomplete
                    sx={{ width: 400 }}
                    size="small"
                    options={commitList}
                    getOptionLabel={(commit) =>
                        `${commit.commit_id}: ${truncate(commit.key_steps)}`
                    }
                    renderOption={(props, option) => (
                        <li {...props}>
                            <Tooltip
                                title={option.key_steps}
                                componentsProps={{
                                    tooltip: {
                                        sx: {
                                            fontSize: '1rem', // or '20px'
                                            maxWidth: 400,
                                        }
                                    }
                                }}
                                arrow>
                                <span>
                                    {option.timestamp} <b>{option.commit_id}</b>
                                    <br />
                                    <b>Commit: </b>{truncate(option.key_steps)}

                                </span>
                            </Tooltip>
                        </li>
                    )}
                    value={selectedCommit}
                    onChange={(event, newValue) => {
                        handleSelectCommit(newValue?.commit_id ?? '')
                    }}
                    renderInput={(params) => <TextField {...params} label="Search Commits" />}
                    isOptionEqualToValue={(option, value) =>
                        option.commit_id === value.commit_id
                    }
                />

            </Stack>

            {/* Main area */}
            <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
                {
                    panels.length > 0 ?
                        <PanelGrid panels={panels} /> :
                        <><Typography>No Files to Show for Selected Commit</Typography></>
                }
            </Box>

            {/* Simulated Drawer */}
            <Collapse in={drawerOpen} orientation="vertical" unmountOnExit>
                <Box
                    sx={{
                        height: '20vh',
                        bgcolor: '#f5f5f5',
                        borderTop: '1px solid #ddd',
                        borderTopLeftRadius: 12,
                        borderTopRightRadius: 12,
                        overflow: 'auto',
                        p: 2,
                    }}
                >
                    <CommitHistory />
                </Box>
            </Collapse>
        </Paper>
    )
}

export default DataPreview
