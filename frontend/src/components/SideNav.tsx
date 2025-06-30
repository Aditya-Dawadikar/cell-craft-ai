import {
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Box,
    Typography,
    Dialog, DialogTitle, DialogContent,
    DialogActions, Button, TextField, InputLabel,
    Autocomplete,
    Tooltip, IconButton, Menu, MenuItem
} from '@mui/material'
import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { useState } from 'react';

import SearchIcon from '@mui/icons-material/Search';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';

import { useSelector, useDispatch } from 'react-redux';
import type { RootState } from '../store/index'
import { createSession } from '../services/session';

import { addSession, setActiveSession } from '../slices/sessionSlice';
import type { Session } from '../interfaces/SessionInterface';
import Logo from '../assets/logo.svg'

const SideNav = () => {

    const navOptions = {
        "NEW_PROJECT": {
            "display_name": "New Project",
            "icon": CreateNewFolderIcon,
        },
        "SEARCH_PROJECT": {
            "display_name": "Search Project",
            "icon": SearchIcon,
        }
    }

    const [dialogOpen, setDialogOpen] = useState(false)
    const [sessionName, setSessionName] = useState("")
    const [selectedFile, setSelectedFile] = useState<File | null>(null)

    const sessionsList = useSelector((state: RootState) => state.session.sessions)
    const activeSession = useSelector((state: RootState) => state.session.activeSession)

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

            dispatch(addSession({
                session_id: response.session_id,
                session_name: response.session_name
            }))

            handleSelectSession({
                session_id: response.session_id,
                session_name: response.session_name
            })

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

    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
    const [menuSession, setMenuSession] = useState<Session | null>(null)

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, session: Session) => {
        setAnchorEl(event.currentTarget)
        setMenuSession(session)
    }

    const handleMenuClose = () => {
        setAnchorEl(null)
        setMenuSession(null)
    }

    return (
        <Box sx={{ width: '100%', height: '100vh', bgcolor: '#f5f5f5' }}>
            <Box sx={{ p: 2 }}>
                <img src={Logo} alt="Logo" style={{ height: 40, margin: "1em 0" }} />
                <List>
                    <ListItem key={navOptions.SEARCH_PROJECT.display_name} disablePadding>
                        <Autocomplete
                            sx={{ width: 400 }}
                            size="small"
                            options={sessionsList}
                            getOptionLabel={(session) =>
                                `${session.session_name}`
                            }
                            renderOption={(props, option) => {
                                const { key, ...rest } = props
                                return (
                                    <Box key={key} component='li' {...rest}>
                                        <Tooltip
                                            title={option.session_name}
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
                                                {option.session_name}
                                            </span>
                                        </Tooltip>
                                    </Box>
                                )
                            }}
                            value={
                                sessionsList.find((s) => s.session_id === activeSession?.session_id) ?? null
                            }
                            onChange={(event, newValue) => {
                                if (newValue) handleSelectSession(newValue)
                            }}
                            renderInput={(params) => <TextField {...params} label="Search Projects" />}
                            isOptionEqualToValue={(option, value) =>
                                option.session_id === value?.session_id
                            }
                        />
                    </ListItem>
                    <br />
                    <ListItem key={navOptions.NEW_PROJECT.display_name} disablePadding>
                        <ListItemButton onClick={() => setDialogOpen(true)}>
                            <ListItemIcon>
                                <navOptions.NEW_PROJECT.icon />
                            </ListItemIcon>
                            <ListItemText primary={navOptions.NEW_PROJECT.display_name} />
                        </ListItemButton>
                    </ListItem>
                </List>

                <Typography variant="h6" sx={{ mt: 3 }}>
                    Projects
                </Typography>

                <List>
                    {sessionsList.map((session, index) => {
                        const isActive = session.session_id === activeSession?.session_id
                        return (
                            <ListItem
                                key={session.session_id}
                                secondaryAction={
                                    <>
                                        <IconButton
                                            edge="end"
                                            aria-label="options"
                                            onClick={(e) => handleMenuOpen(e, session)}
                                        >
                                            <MoreHorizIcon />
                                        </IconButton>
                                    </>
                                }
                                disablePadding
                                sx={{ bgcolor: isActive ? '#e0e0e0' : 'transparent' }}
                            >
                                <ListItemButton onClick={() => handleSelectSession(session)}>
                                    <ListItemText primary={session.session_name} />
                                </ListItemButton>
                            </ListItem>
                        )
                    })}
                </List>
                <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleMenuClose}
                >
                    <MenuItem
                        onClick={() => {
                            console.log('Edit', menuSession)
                            handleMenuClose()
                        }}
                    >
                        <EditIcon />
                        <span style={{ margin: "0px 10px" }}>Edit</span>
                    </MenuItem>
                    <MenuItem
                        onClick={() => {
                            console.log('Delete', menuSession)
                            handleMenuClose()
                        }}
                    >
                        <DeleteIcon />
                        <span style={{ margin: "0px 10px" }}>Delete</span>
                    </MenuItem>
                </Menu>
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