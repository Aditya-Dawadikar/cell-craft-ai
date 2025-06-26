import { List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Box,
    Typography
 } from '@mui/material'
 
import SearchIcon from '@mui/icons-material/Search';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';

const SideNav = () => {

    const navOptions = [{
        "display_name": "New Project",
        "icon": CreateNewFolderIcon,
    },{
        "display_name": "Search Project",
        "icon": SearchIcon,
    }]

    const projects = [{
        "project_name": "Project 0",
        "created_at": "6/25/2025",
        "last_updated_at": "6/25/2025"
    },{
        "project_name": "Project 1",
        "created_at": "6/25/2025",
        "last_updated_at": "6/25/2025"
    },{
        "project_name": "Project 2",
        "created_at": "6/25/2025",
        "last_updated_at": "6/25/2025"
    },]

    return (
        <Box sx={{ width: '100%', height: '100vh', bgcolor: '#f5f5f5' }}>
            <Box sx={{ p:2 }}>
                <Typography variant="h6" gutterBottom>
                    Navigation
                </Typography>
                <List>
                    {navOptions.map((option) => (
                    <ListItem key={option.display_name} disablePadding>
                        <ListItemButton>
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
                    {projects.map((project, index) => (
                    <ListItem key={index} disablePadding>
                        <ListItemButton>
                        <ListItemText primary={project.project_name} />
                        </ListItemButton>
                    </ListItem>
                    ))}
                </List>
            </Box>
        
        </Box>
    )
}

export default SideNav