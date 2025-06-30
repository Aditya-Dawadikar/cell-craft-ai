const BASE_URL = import.meta.env.VITE_BASE_URL

export const sendMessage = async (session_id: string, msg: string): Promise<any> => {
    const formData = new FormData()

    formData.append('session_id', session_id)
    formData.append('query', msg)

    const response = await fetch(`${BASE_URL}/transform_csv/`,{
        method: 'POST',
        body: formData
    })

    if (!response.ok){
        throw new Error("Failed to send form data")
    }

    return await response.json()

}

export const loadConversationHistory = async (session_id: string): Promise<any> =>{
    const response = await fetch(`${BASE_URL}/chat-history?session_id=${session_id}`)

    if (!response.ok){
        throw new Error("Failed to load chat history")
    }

    return await response.json()
}