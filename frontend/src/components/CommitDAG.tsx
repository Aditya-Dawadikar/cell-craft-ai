import React, { useEffect, useState } from 'react'
import ReactFlow, {
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  Position,
  Handle,
  useReactFlow
} from 'reactflow'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState } from '../store'
import { setSelectedCommit } from '../slices/commitSlice'
import type { Node, Edge } from 'reactflow'
import { getVersionHistory } from '../services/commit'
import CircularProgress from '@mui/material/CircularProgress';
import { Box, Typography } from '@mui/material'


// === Custom Commit Node ===
export const CommitNode = ({ data }: { data: any }) => {
  return (
    <div
      style={{
        textAlign: 'left',
        whiteSpace: 'normal',
        overflowWrap: 'break-word',
        maxWidth: 220,
        boxSizing: 'border-box',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#54ffc9',
        border: '2px solid #ccc',
        borderRadius: 8,
        padding: 4,
      }}
    >
      <div>
        <b>Commit ID:</b>{' '}
        <span style={{ background: '#fdff32', padding: '1px 4px', borderRadius: '2px' }}>
          {data.commit_id}
        </span>
      </div>

      <div style={{ fontSize: '0.75rem', marginTop: 2 }}>
        <b>Created at:</b> {data.timestamp}
      </div>

      <div style={{ marginTop: 4 }}>
        <b>Description:</b>
        <span
          style={{
            display: 'block',
            backgroundColor: '#f9f9f9',
            boxShadow: 'inset 1px 1px 3px rgba(0,0,0,0.5)',
            borderRadius: '4px',
            padding: '6px',
            lineHeight: 1.4,
            boxSizing: 'border-box',
            width: '100%',
            marginTop: '2px',
          }}
        >
          {data.key_steps}
        </span>
      </div>

      <Handle type="source" position={Position.Right} id="main" />
      <Handle type="source" position={Position.Bottom} id="files" />
      <Handle type="target" position={Position.Left} id="incoming" />
    </div>
  )
}

const nodeTypes = { commitNode: CommitNode }

const CommitDAG = () => {

  const { fitView } = useReactFlow()

  const dispatch = useDispatch()

  const [commits, setCommits] = useState([])

  const commitHead = useSelector((state: RootState) => state.commit.head)
  const selectedCommit = useSelector((state: RootState) => state.commit.selectedCommit)

  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  const [isLoading, setIsLoading] = useState(false)
  const [isError, SetIsError] = useState(false)


  const nodeSpacingX = 500
  const fileOffsetX = 300
  const fileSpacingY = 50

  const session = useSelector((state: RootState) => state.session.activeSession)
  let sessionIdFromStore = session?.session_id || ""

  const resetView = async () => {

    try {
      if (session?.session_id && session?.session_id != "") {
        setIsLoading(true)
        const data = await getVersionHistory(sessionIdFromStore)

        setCommits(data.commits)

        let initialNodes: Node[] = []
        let initialEdges: Edge[] = []

        data.commits.map((commit: any, idx: number) => {
          const baseX = idx * nodeSpacingX
          const baseY = 100

          // Commit node
          initialNodes.push({
            id: commit.commit_id,
            type: 'commitNode',
            data: { ...commit },
            position: { x: baseX, y: baseY },
          })

          // Parent edge
          if (commit.parent_id) {
            initialEdges.push({
              id: `${commit.parent_id}->${commit.commit_id}`,
              source: commit.parent_id,
              sourceHandle: 'main',
              target: commit.commit_id,
              targetHandle: 'incoming',
              animated: true,
              type: 'smoothstep',
              style: { stroke: '#888' },
            })
          }

          // File nodes
          if (commit.generated_files?.length) {
            commit.generated_files.forEach((file, i) => {
              const fileId = `${commit.commit_id}-file-${i}`

              initialNodes.push({
                id: fileId,
                type: 'default',
                data: { label: file.title },
                position: {
                  x: baseX + fileOffsetX,
                  y: baseY + 100 + i * fileSpacingY,
                },
                targetPosition: Position.Left,
                style: {
                  backgroundColor: '#fef5d3',
                  border: '1px solid #ccc',
                  borderRadius: 4,
                  padding: 6,
                  width: 140,
                  fontSize: '0.75rem',
                  textAlign: 'center',
                },
              })

              initialEdges.push({
                id: `edge-${commit.commit_id}-${fileId}`,
                source: commit.commit_id,
                sourceHandle: 'files',
                target: fileId,
                type: 'smoothstep',
              })
            })
          }
        })

        setNodes(initialNodes)
        setEdges(initialEdges)
        fitView()

        setIsLoading(false)
      }
      else {
        console.log("Session ID not set in store yet")
      }
    } catch (err) {
      setIsLoading(false)
      SetIsError(true)
      console.log("Error fetching version history:", err)
    }

  }

  useEffect(() => {
    resetView()
  }, [session])

  useEffect(() => {
    if (!selectedCommit) return

    // TODO: this color highlight is not working
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === selectedCommit.commit_id) {
          return {
            ...node,
            style: {
              ...node.style,
              borderColor: 'blue',
            },
          }
        }
        return {
          ...node
        }
      })
    )
    resetView()
  }, [selectedCommit, commitHead])

  return (
    <div style={{ width: '100%', height: "100%", overflow: 'auto' }}>
      {
        isLoading === true ? <Box
          sx={{
            flexGrow: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: "100%"
          }}>
          <CircularProgress disableShrink />
        </Box> : isError === true ? <Box
          sx={{
            height: "100%", flexGrow: 1, overflow: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
          <Typography variant="h6" color="textSecondary">
            Something went wrong ¯\_(ツ)_/¯
          </Typography>
        </Box> : <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          panOnScroll
          zoomOnScroll
          nodeTypes={nodeTypes}
          onNodeClick={(_, node) => {
            const selected = commits.find((c) => c.commit_id === node.id)
            if (selected) {
              dispatch(setSelectedCommit(selected))
            }
          }}
        >
          <Background />
          <Controls />
        </ReactFlow>
      }

    </div>
  )
}

export default CommitDAG
