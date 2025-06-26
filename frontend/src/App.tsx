import './App.css'
import DataPreview from './components/DataPreview'

import SideNav from './components/SideNav'
import {Grid} from '@mui/material'
import Chat from './components/Chat'

function App() {

  return (
    <>
      <Grid container spacing={2}>
        <Grid size={2}>
          <SideNav/>
        </Grid>
        <Grid size={4}>
          <Chat/>
        </Grid>
        <Grid size={6}>
          <DataPreview/>
        </Grid>
      </Grid>
    </>
  )
}

export default App
