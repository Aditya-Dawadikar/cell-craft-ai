import React, { useEffect } from 'react'
import ReactFlow, {
  ReactFlowProvider,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  Position,
  Handle
} from 'reactflow'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState } from '../store'
import { setSelectedCommit } from '../slices/commitSlice'
import type { Node, Edge } from 'reactflow'

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
  const dispatch = useDispatch()

  const commits = useSelector((state: RootState) => state.commit.commits)
  const commitHead = useSelector((state: RootState) => state.commit.head)
  const selectedCommit = useSelector((state: RootState) => state.commit.selectedCommit)

  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])


  const nodeSpacingX = 500
  const fileOffsetX = 300
  const fileSpacingY = 50

  const session = useSelector((state: RootState) => state.session.activeSession)

  useEffect(() => {
    setNodes([])
    setEdges([])
  }, [session?.session_id])

  useEffect(() => {
    const initialNodes: Node[] = []
    const initialEdges: Edge[] = []

    commits.forEach((commit, idx) => {
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
  }, [commits])

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
  }, [selectedCommit, commitHead])

  return (
    <ReactFlowProvider>
      <div style={{ width: '100%', height: '100%', overflow: 'auto' }}>
        <ReactFlow
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
      </div>
    </ReactFlowProvider>
  )
}

export default CommitDAG
