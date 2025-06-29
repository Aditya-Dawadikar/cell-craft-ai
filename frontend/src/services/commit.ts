export const getVersionHistory = async (session_id: string): Promise<any> => {

    const response = await fetch(`http://localhost:8000/version-history/?session_id=${session_id}`)

    if (!response.ok){
        throw new Error("Failed to fetch Version History")
    }

    return await response.json()

}

export const getCommitFiles = async(session_id: string, commit_id: string): Promise<any>=>{
    const response = await fetch(`http://localhost:8000/list_commit_files?session_id=${session_id}&commit_id=${commit_id}`)

    if (!response.ok){
        throw new Error("Failed to fetch commit files")
    }

    return await response.json()
}
