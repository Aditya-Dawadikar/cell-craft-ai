import { Box, Button, Collapse, Paper, Stack } from '@mui/material'
import CommitHistory from './DataTiles/CommitHistory'
import { useEffect, useState } from 'react'
import PanelGrid from './DataTiles/PanelGrid'
import { Tooltip } from '@mui/material'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState } from '../store/index'
import { Autocomplete, Typography, TextField } from '@mui/material'
import { getCommitFiles } from '../services/commit'
import { setSelectedCommit } from '../slices/commitSlice'
import type { Commit } from '../interfaces/CommitInterfance'
import CommitDAG from './CommitDAG'
import CommitIcon from '@mui/icons-material/Commit';

type Panel =
    | { type: 'dataframe'; title: string; url: string }
    | { type: 'readme'; title: string; url: string }
    | { type: 'chart'; title: string; url: string }

const DataPreview = () => {

    const dispatch = useDispatch()

    const [drawerOpen, setDrawerOpen] = useState(true)

    const commitList = useSelector((state: RootState) => state.commit.commits) ?? []
    const commitHead = useSelector((state: RootState) => state.commit.head)
    const selectedCommit = useSelector((state: RootState) => state.commit.selectedCommit)

    const sessionIdFromStore = useSelector((state: RootState) => state.chat.session_id)

    const [panels, setPanels] = useState<Panel[]>([])


    const truncate = (str: string | undefined | null, len = 50) =>
        str && str.length > len ? str.slice(0, len) + '...' : str ?? ''

    useEffect(() => {
        if (selectedCommit !== null && selectedCommit?.commit_id !== null) {
            handleFetchFiles(selectedCommit.commit_id)
        }
    }, [selectedCommit])

    const handleFetchFiles = async (commit_id: string) => {
        if (sessionIdFromStore && commit_id) {

            const data = await getCommitFiles(sessionIdFromStore, commit_id)

            console.log("commit files", data)

            setPanels([...data.files])
        }
    }

    const handleSelectCommit = (commit: Commit | null) => {
        if (commit != null) {
            dispatch(setSelectedCommit(commit))
            handleFetchFiles(commit.commit_id)
        } else {
            dispatch(setSelectedCommit(null))
            // clear the display too
            setPanels([])
        }
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
                    <CommitIcon />
                </Button>

                <Autocomplete
                    sx={{ width: 400 }}
                    size="small"
                    options={commitList}
                    getOptionLabel={(commit) =>
                        `${commit.commit_id}: ${truncate(commit.key_steps)}`
                    }
                    renderOption={(props, option) => {
                        const { key, ...rest } = props
                        return (
                            <Box key={key} component='li' {...rest}>
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
                                    placement="left"
                                    arrow>
                                    <span>
                                        {option.timestamp} <b>{option.commit_id}</b>
                                        <br />
                                        <b>Commit: </b>{truncate(option.key_steps)}

                                    </span>
                                </Tooltip>
                            </Box>
                        )
                    }}
                    value={commitList.find(c => c.commit_id === selectedCommit?.commit_id) ?? null}
                    onChange={(event, newValue) => {
                        handleSelectCommit(newValue)
                    }}
                    renderInput={(params) => <TextField {...params} label="Search Commits" />}
                    isOptionEqualToValue={(option, value) =>
                        option.commit_id === value?.commit_id
                    }
                />

            </Stack>

            {/* Main area */}
            <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
                {
                    panels.length > 0 ?
                        <PanelGrid panels={panels} /> :
                        <><Typography>No Files to Show. Select a commit.</Typography></>
                }
            </Box>

            {/* Simulated Drawer */}
            <Collapse in={drawerOpen} orientation="vertical" unmountOnExit>
                <Box
                    sx={{
                        height: '50vh',
                        bgcolor: '#f5f5f5',
                        borderTop: '1px solid #ddd',
                        borderTopLeftRadius: 12,
                        borderTopRightRadius: 12,
                        overflow: 'auto',
                        p: 2,
                    }}
                >
                    <CommitDAG />
                </Box>
            </Collapse>
        </Paper>
    )
}

export default DataPreview
