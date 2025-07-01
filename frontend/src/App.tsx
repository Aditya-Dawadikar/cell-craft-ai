import './App.css'
import DataPreview from './components/DataPreview'

import SideNav from './components/SideNav'
import { Grid } from '@mui/material'
import Chat from './components/Chat'

import { getSessionList } from './services/session'
import { useDispatch } from 'react-redux'
import { loadSessions } from './slices/sessionSlice'
import { useEffect } from 'react'

function App() {

  const dispatch = useDispatch()

  const loadSessionList = async () => {
    const data = await getSessionList()
    dispatch(loadSessions(data))
  }

  useEffect(() => {
    loadSessionList()
  }, [])

  return (
    <>
      <Grid container spacing={1}>
        <Grid size={2}>
          <SideNav />
        </Grid>
        <Grid size={4}>
          <Chat />
        </Grid>
        <Grid size={6}>
          <DataPreview />
        </Grid>
      </Grid>
    </>
  )
}

export default App
