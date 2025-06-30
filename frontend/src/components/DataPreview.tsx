import { Box, Paper, Stack } from '@mui/material'
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
import { ReactFlowProvider } from 'reactflow'
import Split from 'react-split'

type Panel =
    | { type: 'dataframe'; title: string; url: string }
    | { type: 'readme'; title: string; url: string }
    | { type: 'chart'; title: string; url: string }

const DataPreview = () => {

    const dispatch = useDispatch()

    const commitList = useSelector((state: RootState) => state.commit.commits) ?? []
    const commitHead = useSelector((state: RootState) => state.commit.head)
    const selectedCommit = useSelector((state: RootState) => state.commit.selectedCommit)

    const session = useSelector((state: RootState) => state.session.activeSession)
    let sessionIdFromStore = session?.session_id || ""

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

    useEffect(() => {
        // Clear panels when the session changes
        setPanels([]);
    }, [sessionIdFromStore]);

    return (
        <Paper
            elevation={2}
            sx={{
                height: '100%',
                maxHeight: 'calc(100vh - 30px)',
                p: 1,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
            }}
            style={{ margin: "0.5em" }}
        >
            <Stack direction="row" spacing={2} mb={2}>

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
            <Split
                direction="vertical"
                sizes={[50, 50]}
                minSize={100}
                gutterSize={8}
                className="split"
                style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
            >
                <Box sx={{ flexGrow: 1, overflow: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {panels.length > 0 ? (
                        <PanelGrid panels={panels} />
                    ) : (
                        <Typography variant="h6" color="textSecondary">
                            No Files to Show. Select a commit.
                        </Typography>
                    )}
                </Box>
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
                    <ReactFlowProvider>
                        <CommitDAG key={session?.session_id || 'default'} />
                    </ReactFlowProvider>
                </Box>
            </Split>
        </Paper>
    )
}

export default DataPreview
