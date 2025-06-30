const BASE_URL = import.meta.env.VITE_BASE_URL

export const getSessionList = async (): Promise<any> => {
    const response = await fetch(`${BASE_URL}/session-list`)

    if (!response.ok) {
        throw new Error("Failed to fetch sessions")
    }

    return await response.json()
}

export const createSession = async (file: File, sessionName: string): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file)
    formData.append('session_name', sessionName)

    const response = await fetch(`${BASE_URL}/create-session/`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error("Failed to create session");
    }

    return await response.json();
}