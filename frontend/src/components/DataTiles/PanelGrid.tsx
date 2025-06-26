import { Grid, Paper, Typography, Box } from '@mui/material'
import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import Papa from 'papaparse'

type Panel =
    | { type: 'dataframe'; title: string; url: string }
    | { type: 'readme'; title: string; url: string }
    | { type: 'chart'; title: string; url: string }

interface Props {
    panels: Panel[]
}

const PanelGrid = ({ panels }: Props) => {
    return (
        <Grid container spacing={2}>
            {panels.map((panel, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                    <Paper elevation={3} sx={{ m: 1, height: '100%' }}>
                        <div style={{padding:"1em"}}>
                            <Typography variant="h6" gutterBottom>
                                {panel.title}
                            </Typography>

                            {panel.type === 'dataframe' && <CSVPreview url={panel.url} />}
                            {panel.type === 'readme' && <MarkdownFromUrl url={panel.url} />}
                            {panel.type === 'chart' && (
                                <Box
                                    component="img"
                                    src={panel.url}
                                    alt={panel.title}
                                    sx={{ width: '100%', maxHeight: 300, objectFit: 'contain' }}
                                />
                            )}
                        </div>
                    </Paper>
                </Grid>
            ))}
        </Grid>
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
            .catch(() => setError('Failed to load CSV'))
    }, [url])

    if (error) return <Typography color="error">{error}</Typography>

    return (
        <Box
            component="table"
            sx={{
                width: '100%',
                borderCollapse: 'collapse',
                '& td, & th': {
                    border: '1px solid #ddd',
                    padding: '4px',
                    fontSize: '0.75rem',
                },
            }}
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
            <div style={{background:"#ffeede", padding: "1em"}}>
                <ReactMarkdown>{markdown}</ReactMarkdown>
            </div>
        </Box>
    )
}


export default PanelGrid
