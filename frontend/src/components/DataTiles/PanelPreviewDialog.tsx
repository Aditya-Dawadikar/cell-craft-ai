import {
    Dialog,
    AppBar,
    Toolbar,
    IconButton,
    Typography,
    Button,
    Box
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import DownloadIcon from '@mui/icons-material/Download'
// import type { Panel } from '../types/PanelTypes'  // Adjust path as needed

export type Panel =
    | { type: 'dataframe'; title: string; url: string }
    | { type: 'readme'; title: string; url: string }
    | { type: 'chart'; title: string; url: string }


interface PanelPreviewDialogProps {
    panel: Panel | null
    onClose: () => void
}

const BASE_URL = import.meta.env.VITE_BASE_URL

const PanelPreviewDialog = ({ panel, onClose }: PanelPreviewDialogProps) => {
    if (!panel) return null

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="xl"
            PaperProps={{
                sx: {
                    width: '80vw',
                    height: '80vh',
                    maxWidth: 'none',
                    borderRadius: 3,
                    boxShadow: 6,
                    position: 'relative'
                }
            }}>
            <AppBar position="relative">
                <Toolbar>
                    <IconButton edge="start" color="inherit" onClick={onClose}>
                        <CloseIcon />
                    </IconButton>
                    <Typography sx={{ ml: 2, flex: 1 }} variant="h6">
                        {panel.title}
                    </Typography>
                    <Button
                        color="inherit"
                        href={panel.url}
                        download
                        target="_blank"
                        rel="noopener"
                        startIcon={<DownloadIcon />}
                    >
                        Download
                    </Button>
                </Toolbar>
            </AppBar>

            <Box p={4} sx={{ overflow: 'auto' }}>
                {panel.type === 'dataframe' && (
                    <iframe src={BASE_URL + panel.url} style={{ width: '100%', height: '90vh', border: 'none' }} />
                )}
                {panel.type === 'readme' && (
                    <iframe src={BASE_URL + panel.url} style={{ width: '100%', height: '90vh', border: 'none' }} />
                )}
                {panel.type === 'chart' && (
                    <img src={BASE_URL + panel.url} alt="Chart Preview" style={{ maxWidth: '100%' }} />
                )}
            </Box>
        </Dialog>
    )
}

export default PanelPreviewDialog
