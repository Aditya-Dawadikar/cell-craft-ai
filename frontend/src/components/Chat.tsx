import { useState, useRef, useEffect } from 'react'
import { Paper, Typography } from '@mui/material'
import { Box } from '@mui/material'
import { Divider } from '@mui/material'
import { TextField } from '@mui/material'
import { IconButton } from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import { sendMessage, loadConversationHistory } from '../services/chat'
import { LinearProgress } from '@mui/material'
import { useDispatch, useSelector } from 'react-redux'
import type { RootState } from '../store/index'
import { addMessage, setConversation } from '../slices/chatSlice'
import type { ChatMessage } from '../interfaces/ChatMessageInterface'
import { setCommitHistory, setSelectedCommit } from '../slices/commitSlice'
import { getVersionHistory } from '../services/commit'

interface Message {
    text: string
    sender: 'user' | 'bot',
    uploadedFile?: File;
    generatedFiles?: {
        title: string
        url: string
        type?: string
    }[],
    commitData?: {
        commit_id: string,
        parent_id: string,
        timestamp: string
    }
}

const Chat = () => {

    const messages = useSelector((state: RootState) => state.chat.messages)
    const session = useSelector((state: RootState) => state.session.activeSession)
    let sessionIdFromStore = session?.session_id || ""

    const commitHistoryFromStore = useSelector((state: RootState) => state.commit.commits)
    const commitHeadFromStore = useSelector((state: RootState) => state.commit.head)

    const dispatch = useDispatch()

    const [isLoading, setIsLoading] = useState<Boolean>(false)
    const [versionHistory, setVersionHistory] = useState<any>({
        head: null,
        commits: []
    })

    const [attachedFile, setAttachedFile] = useState<File | null>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)
    const bottomRef = useRef<HTMLDivElement>(null)

    const [input, setInput] = useState('')

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

        input.trim()

        const newMsg: Message = {
            text: input,
            sender: 'user',
            uploadedFile: attachedFile || undefined,
        };

        dispatch(addMessage({
            text: input,
            sender: 'user',
        } as ChatMessage));

        setInput('')
        clearAttachment();

        try {
            setIsLoading(true)
            const result = await sendMessage(sessionIdFromStore, input)

            dispatch(addMessage({
                text: result.response,
                sender: 'bot',
                generated_files: result.generated_files,
                commit_data: result.commit_data
            } as ChatMessage))

            await pollHistory()

            if (result.mode === "CODE") {
                dispatch(setSelectedCommit(result.commit_data))
            }

            setIsLoading(false)
        } catch (err) {
            console.log(err)
            setIsLoading(false)
            dispatch(addMessage({
                text: "Some Error Occurred, Try again",
                sender: 'bot'
            }))
        }

    }


    const fetchConversation = async () => {
        try {
            const data = await loadConversationHistory(sessionIdFromStore)
            let conv: ChatMessage[] = []
            data["chat_history"].map((item: any, index) => {
                let userMessage = {
                    text: item.query,
                    sender: 'user',
                }
                let botMessage = {
                    text: item.response,
                    sender: 'bot',
                    generatedFiles: item.generated_files,
                    commitData: {
                        commit_id: item.commit_id,
                        parent_id: item.parent_commit,
                        timestamp: item.timestamp
                    }
                }
                conv.push(userMessage)
                conv.push(botMessage)
            })
            dispatch(setConversation(conv))

        } catch (err) {
            console.log(err)
        }
    }

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

    useEffect(() => {

        fetchConversation()

        pollHistory()

        const intervalId = setInterval(pollHistory, 6 * 10 * 1000)

        return () => { clearInterval(intervalId) }
    }, [])

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, isLoading])

    useEffect(() => {
        if (!sessionIdFromStore) return;

        fetchConversation();
        pollHistory();
    }, [sessionIdFromStore]);

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
                            display: 'flex',
                            flexDirection: 'column',
                            alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                            alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                        }}
                    >
                        {/* Message Bubble */}
                        <Box
                            sx={{
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

                        {/* User uploaded file */}
                        {msg.uploadedFile && (
                            <Box
                                mt={0.5}
                                p={1}
                                width={160}
                                bgcolor="#e0f7fa"
                                borderRadius={1}
                                sx={{ color: 'black', textAlign: 'right' }}
                            >
                                <Typography variant="caption" fontWeight="bold">
                                    {msg.uploadedFile.name}
                                </Typography>
                            </Box>
                        )}

                        {/* Bot generated files */}
                        {
                            msg.commitData ? <Box
                                bgcolor="#54ffc9"
                                p={1}
                                m={1}
                                borderRadius={1}
                                sx={{ cursor: "pointer" }}
                                onClick={() => {
                                    if (msg.commitData) {
                                        dispatch(setSelectedCommit(msg.commitData));
                                    }
                                }}>
                                {msg.commitData ? <>
                                    <Typography variant="caption" fontWeight="bold" >
                                        Commit ID: <span style={{ background: '#fdff32', padding: '1px 4px', borderRadius: '2px' }}>{msg.commitData.commit_id}</span>
                                    </Typography>
                                </> : <></>}
                                {msg.generatedFiles?.length > 0 &&
                                    msg.generatedFiles.map((file, fileIdx) => (
                                        <Box
                                            key={fileIdx}
                                            mt={0.5}
                                            p={1}
                                            width={180}
                                            bgcolor="#fef5d3"
                                            borderRadius={1}
                                            sx={{ color: 'black', textAlign: 'left' }}
                                        >
                                            <Typography variant="caption"
                                                sx={{ whiteSpace: 'normal', wordBreak: 'break-word' }}>
                                                {file.title}
                                            </Typography>
                                        </Box>
                                    ))}
                            </Box> : <></>
                        }

                    </Box>
                ))}
                <div ref={bottomRef} />
                {
                    isLoading ? <LinearProgress /> : <></>
                }
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