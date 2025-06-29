import {
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Box,
    Typography,
    Dialog, DialogTitle, DialogContent,
    DialogActions, Button, TextField, InputLabel
} from '@mui/material'

import { useState } from 'react';

import SearchIcon from '@mui/icons-material/Search';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';

import { useSelector, useDispatch } from 'react-redux';
import type { RootState } from '../store/index'
import { createSession } from '../services/session';

import { addSession, setActiveSession } from '../slices/sessionSlice';
import type { Session } from '../interfaces/SessionInterface';

const SideNav = () => {

    const navOptions = [{
        "display_name": "New Project",
        "icon": CreateNewFolderIcon,
    }, {
        "display_name": "Search Project",
        "icon": SearchIcon,
    }]

    const [dialogOpen, setDialogOpen] = useState(false)
    const [sessionName, setSessionName] = useState("")
    const [selectedFile, setSelectedFile] = useState<File | null>(null)

    const sessionsList = useSelector((state: RootState) => state.session.sessions)

    const dispatch = useDispatch()

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) setSelectedFile(file)
    }

    const handleCreateSession = async () => {
        try {
            if (!selectedFile || !sessionName) {
                alert("Please provide both session name and CSV file.")
                return
            }
            const response = await createSession(selectedFile, sessionName)
            console.log("Session created:", response.session_id)

            dispatch(addSession({
                session_id: response.session_id,
                session_name: response.session_name
            }))

            setDialogOpen(false)
            setSessionName("")
            setSelectedFile(null)
        } catch (error) {
            console.error("Error creating session:", error)
        }
    }

    const handleSelectSession = async (selectedSession: Session) => {

        dispatch(setActiveSession({
            session_id: selectedSession.session_id,
            session_name: selectedSession.session_name
        }))
    }

    return (
        <Box sx={{ width: '100%', height: '100vh', bgcolor: '#f5f5f5' }}>
            <Box sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                    Navigation
                </Typography>
                <List>
                    {navOptions.map((option) => (
                        <ListItem key={option.display_name} disablePadding>
                            <ListItemButton onClick={() => setDialogOpen(true)}>
                                <ListItemIcon>
                                    <option.icon />
                                </ListItemIcon>
                                <ListItemText primary={option.display_name} />
                            </ListItemButton>
                        </ListItem>
                    ))}
                </List>

                <Typography variant="h6" sx={{ mt: 3 }}>
                    Projects
                </Typography>
                <List>
                    {sessionsList.map((session, index) => (
                        <ListItem key={session.session_id} disablePadding>
                            <ListItemButton onClick={() => {
                                handleSelectSession(session)
                            }}>
                                <ListItemText primary={session.session_name} />
                            </ListItemButton>
                        </ListItem>
                    ))}
                </List>
            </Box>

            {/* Dialog Box */}
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New Project</DialogTitle>
                <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
                    <TextField
                        label="Session Name"
                        value={sessionName}
                        onChange={(e) => setSessionName(e.target.value)}
                        fullWidth
                    />
                    <InputLabel>Upload CSV File</InputLabel>
                    <input type="file" accept=".csv" onChange={handleFileChange} />
                    {selectedFile && <Typography variant="caption">Selected: {selectedFile.name}</Typography>}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
                    <Button variant="contained" onClick={handleCreateSession}>Create</Button>
                </DialogActions>
            </Dialog>

        </Box>
    )
}

export default SideNav