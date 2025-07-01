import { Grid, Paper, Typography, Box, Stack, IconButton } from '@mui/material'
import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import Papa from 'papaparse'
import DownloadIcon from '@mui/icons-material/Download';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import PanelPreviewDialog from './PanelPreviewDialog';

type Panel =
    | { type: 'dataframe'; title: string; url: string }
    | { type: 'readme'; title: string; url: string }
    | { type: 'chart'; title: string; url: string }

interface Props {
    panels: Panel[]
}


const PanelGrid = ({ panels }: Props) => {

    const [enlargedPanel, setEnlargedPanel] = useState<Panel | null>(null)

    const handleDownload = async (url: string, filename: string) => {
        try {
            const response = await fetch(url)
            const blob = await response.blob()

            const blobUrl = window.URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = blobUrl
            link.download = filename
            document.body.appendChild(link)
            link.click()

            // Cleanup
            document.body.removeChild(link)
            window.URL.revokeObjectURL(blobUrl)
        } catch (err) {
            console.error('Download failed:', err)
        }
    }

    return (
        <>
            <Grid container spacing={2}>
                {panels.map((panel, index) => (
                    <Grid item xs={12} sm={12} md={12} key={index}>
                        <Paper elevation={3} sx={{ m: 1 }}>
                            <Stack
                                m={1}
                                direction="row"
                                alignItems="center"
                                justifyContent="space-between">
                                <Typography gutterBottom>
                                    {panel.title}
                                </Typography>
                                <Stack direction="row"
                                    sx={{
                                        justifyContent: 'flex-end'
                                    }}>

                                    <IconButton>
                                        <FullscreenIcon onClick={() => { setEnlargedPanel(panel) }} />
                                    </IconButton>
                                    <IconButton onClick={() => { handleDownload(panel.url, panel.title) }}>
                                        <DownloadIcon />
                                    </IconButton>
                                </Stack>
                            </Stack>

                            <Box m={1}>
                                {panel.type === 'dataframe' && <CSVPreview url={panel.url} />}
                                {panel.type === 'readme' && <MarkdownFromUrl url={panel.url} />}
                                {panel.type === 'chart' && <ImageFromUrl url={panel.url} title={panel.title} />}
                            </Box>
                        </Paper>
                    </Grid>
                ))}
            </Grid>
            <PanelPreviewDialog panel={enlargedPanel} onClose={() => setEnlargedPanel(null)} />
        </>
    )
}

const CSVPreview = ({ url }: { url: string }) => {
    const [rows, setRows] = useState<string[][]>([])
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetch(url)
            .then((res) => res.text())
            .then((csv) => {
                const result = Papa.parse<string[]>(csv, { skipEmptyLines: true })
                if (result.data && result.data.length > 0) {
                    setRows(result.data as string[][])
                } else {
                    setError('Empty CSV')
                }
            })
            .catch((err) => setError(`Failed to load CSV \n${err}`))
    }, [url])

    if (error) return <Typography color="error">{error}</Typography>

    return (
        <Box
            sx={{ maxHeight: 300, overflowY: 'auto' }}
            component="table"
        >
            <thead>
                <tr>
                    {rows[0]?.map((col, i) => (
                        <th key={i}>{col}</th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {rows.slice(1, 6).map((row, i) => (
                    <tr key={i}>
                        {row.map((cell, j) => (
                            <td key={j}>{cell}</td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </Box>
    )
}

const MarkdownFromUrl = ({ url }: { url: string }) => {
    const [markdown, setMarkdown] = useState('Loading...')

    useEffect(() => {
        fetch(url)
            .then((res) => res.text())
            .then(setMarkdown)
            .catch(() => setMarkdown('Failed to load markdown'))
    }, [url])

    return (
        <Box sx={{ maxHeight: 300, overflowY: 'auto' }}>
            <ReactMarkdown>
                {markdown}
            </ReactMarkdown>
        </Box>
    )
}

const ImageFromUrl = ({ url, title }: { url: string, title: string }) => {
    return (<Box
        component="img"
        src={url}
        alt={title}
        sx={{ maxHeight: 300 }}
    />)
}

export default PanelGrid
