import { Box, Button, Collapse, Paper, Stack } from '@mui/material'
import CommitHistory from './DataTiles/CommitHistory'
import { useState } from 'react'
import PanelGrid from './DataTiles/PanelGrid'

type Panel =
  | { type: 'dataframe'; title: string; url: string }
  | { type: 'readme'; title: string; url: string }
  | { type: 'chart'; title: string; url: string }

const DataPreview = () => {
    const [drawerOpen, setDrawerOpen] = useState(false)

    const panels: Panel[] = [
        {
            type: 'dataframe',
            title: 'Sample DF',
            url: 'http://localhost:8000/static/session_files/e73358fc-2da7-44d5-8d05-7a5d85b124f2/41d3160a/41d3160a.csv',
        },
        {
            type: 'readme',
            title: 'README.md',
            url: 'http://localhost:8000/static/session_files/e73358fc-2da7-44d5-8d05-7a5d85b124f2/1868ec24/readme.md',
        },
        {
            type: 'chart',
            title: 'Chart 1',
            url: 'http://localhost:8000/static/session_files/e73358fc-2da7-44d5-8d05-7a5d85b124f2/29f2af68/total_spent_by_date.png',
        },
    ]


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
            </Stack>

            {/* Main area */}
            <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
                <PanelGrid panels={panels} />
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
