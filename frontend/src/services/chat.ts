export const sendMessage = async (session_id: string, msg: string): Promise<any> => {
    const formData = new FormData()

    formData.append('session_id', session_id)
    formData.append('query', msg)

    const response = await fetch('http://localhost:8000/transform_csv/',{
        method: 'POST',
        body: formData
    })

    if (!response.ok){
        throw new Error("Failed to send form data")
    }

    return await response.json()

}