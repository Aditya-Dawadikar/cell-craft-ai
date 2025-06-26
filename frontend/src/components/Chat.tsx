import { useState } from 'react'
import { Paper, Typography } from '@mui/material'
import { Box } from '@mui/material'
import { Divider } from '@mui/material'
import {TextField} from '@mui/material'
import {IconButton} from '@mui/material'
import SendIcon from '@mui/icons-material/Send';

interface Message {
    text: string
    sender: 'user' | 'bot'
}

const Chat = () => {
    const [messages, setMessages] = useState<Message[]>([
        { text: 'Hi! How can I help you today?', sender: 'bot' },
    ])
    const [input, setInput] = useState('')

    const handleSend = () => {
        if (!input.trim()) return

        setMessages([...messages, { text: input, sender: 'user' }])
        setInput('')
        // Simulate bot reply
        setTimeout(() => {
            setMessages((prev) => [...prev, { text: 'Let me think about that...', sender: 'bot' }])
        }, 800)
    }
    
    return (
        <Paper
            elevation={2}
            sx={{
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
                maxHeight: 'calc(100vh - 32px)',
                p: 1,
                m: 1,
            }}
        >
            <Box
                sx={{
                    flexGrow: 1,
                    overflowY: 'auto',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 1,
                    px: 1,
                    pb: 2,
                }}
            >
                {messages.map((msg, idx) => (
                    <Box
                        key={idx}
                        sx={{
                            alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                            bgcolor: msg.sender === 'user' ? '#1976d2' : '#f1f1f1',
                            color: msg.sender === 'user' ? 'white' : 'black',
                            px: 2,
                            py: 1,
                            borderRadius: 2,
                            maxWidth: '75%',
                        }}
                    >
                        <Typography variant="body2">{msg.text}</Typography>
                    </Box>
                ))}
            </Box>
            <Divider />
            <Box
                sx={{
                    display: 'flex',
                    gap: 1,
                    mt: 1,
                }}
            >
                <TextField
                    fullWidth
                    size="small"
                    placeholder="Type a message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSend()
                    }}
                />
                <IconButton color="primary" onClick={handleSend}>
                    <SendIcon />
                </IconButton>
            </Box>
        </Paper>
    )
}

export default Chat