import { useState, useRef, useEffect } from 'react'
import { Paper, Typography } from '@mui/material'
import { Box } from '@mui/material'
import { Divider } from '@mui/material'
import { TextField } from '@mui/material'
import { IconButton } from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import AttachFileIcon from '@mui/icons-material/AttachFile'
import ClearIcon from '@mui/icons-material/Clear'
import { sendMessage } from '../services/chat'
import { LinearProgress } from '@mui/material'
import { useDispatch, useSelector } from 'react-redux'
import type { RootState } from '../store/index'
import { addMessage } from '../slices/chatSlice'
import type { ChatMessage } from '../interfaces/ChatMessageInterface'
import { setCommitHistory } from '../slices/commitSlice'
import { getVersionHistory } from '../services/commit'

interface Message {
    text: string
    sender: 'user' | 'bot'
}

const Chat = () => {

    const messagesFromStore = useSelector((state: RootState) => state.chat.messages)
    const sessionIdFromStore = useSelector((state: RootState) => state.chat.session_id)

    const commitHistoryFromStore = useSelector((state: RootState) => state.commit.commits)
    const commitHeadFromStore = useSelector((state: RootState) => state.commit.head)

    const dispatch = useDispatch()

    const [isLoading, setIsLoading] = useState<Boolean>(false)
    const [versionHistory, setVersionHistory] = useState<any>({
        head: null,
        commits: []
    })
    const [messages, setMessages] = useState<Message[]>([
        { text: 'Hi! How can I help you today?', sender: 'bot' },
    ])

    const [attachedFile, setAttachedFile] = useState<File | null>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const [input, setInput] = useState('')

    const session_id = "e73358fc-2da7-44d5-8d05-7a5d85b124f2"

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) setAttachedFile(file)
    }

    const openFileDialog = () => {
        fileInputRef.current?.click()
    }

    const clearAttachment = () => {
        setAttachedFile(null)
        if (fileInputRef.current) fileInputRef.current.value = ''
    }

    const handleSend = async () => {
        if (!input.trim()) return

        setMessages([...messages, { text: input, sender: 'user' }])

        dispatch(addMessage({
            text: input,
            sender: 'user'
        } as ChatMessage))

        setInput('')

        try {
            setIsLoading(true)
            const result = await sendMessage(sessionIdFromStore, input)

            setMessages((prev) => [...prev, { text: result.response, sender: 'bot' }])

            dispatch(addMessage({
                text: result.response,
                sender: 'bot'
            } as ChatMessage))

            let generated_files = result.generated_files

            console.log(generated_files)

            setIsLoading(false)
        } catch (err) {
            console.log(err)
        }

    }

    const handleAttachment = async () => {

    }

    useEffect(() => {
        const pollHistory = async () => {
            try {
                const data = await getVersionHistory(sessionIdFromStore)

                setVersionHistory({
                    head: data.head || null,
                    commits: data.commits || []
                })

                dispatch(setCommitHistory({
                    head: data.head || null,
                    commits: data.commits || []
                }))

            } catch (err) {
                console.log("Error fetching version history:", err)
            }
        }

        pollHistory()

        const intervalId = setInterval(pollHistory, 10 * 1000)

        return () => { clearInterval(intervalId) }
    }, [])

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
                {
                    isLoading ? <LinearProgress /> : <></>
                }
            </Box>
            <Divider />

            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                style={{ display: 'none' }}
            />

            {/* Preview */}
            {attachedFile && (
                <Box mt={1} p={1} bgcolor="#f0f0f0" borderRadius={2}>
                    <div style={{ display: "flex" }}>
                        <Typography variant="body2" fontWeight="bold">
                            Attached: {attachedFile.name}
                        </Typography>
                        <IconButton onClick={clearAttachment} size="small">
                            <ClearIcon />
                        </IconButton>
                    </div>
                </Box>
            )}

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
                <IconButton color="primary" onClick={openFileDialog}>
                    <AttachFileIcon />
                </IconButton>
            </Box>
        </Paper>
    )
}

export default Chat