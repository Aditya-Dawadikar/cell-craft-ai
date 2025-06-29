import React, { useState, useEffect, useCallback } from 'react'
import ReactFlow, { ReactFlowProvider, Background, Controls, useNodesState, useEdgesState, Position } from 'reactflow'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState } from '../store'
import { setSelectedCommit } from '../slices/commitSlice'
import type { Node, Edge } from 'reactflow'

const CommitDAG = () => {

  const dispatch = useDispatch()

  const sessionId = useSelector((state: RootState) => state.chat.session_id)

  const commits = useSelector((state: RootState) => state.commit.commits)
  const commitHead = useSelector((state: RootState) => state.commit.head)
  const selectedCommit = useSelector((state: RootState) => state.commit.selectedCommit)

  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  const nodeBackgroundColor = '#54ffc9'
  const selectedNodeBackgroundColor = '#ffe878'

  useEffect(() => {
    const nodeSpacing = 200

    const initialNodes: Node[] = commits.map((commit, idx) => ({
      id: commit.commit_id,
      data: {
        label: (
          <div
            style={{
              textAlign: 'left',
              whiteSpace: 'normal',
              overflowWrap: 'break-word',
              width: '100%',
              boxSizing: 'border-box',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <div>
              <b>Commit ID:</b>{' '}
              <span style={{ background: '#fdff32', padding: '1px 4px', borderRadius: '2px' }}>
                {commit.commit_id}
              </span>
            </div>

            <div style={{ fontSize: '0.75rem', marginTop: 2 }}>
              <b>Created at:</b> {commit.timestamp}
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
                {commit.key_steps}
              </span>
            </div>
          </div>
        )
      },
      position: { x: idx * nodeSpacing, y: 100 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      style: {
        border: '2px solid',
        borderColor: commit.commit_id === commitHead?.commit_id ? 'red' : '#ccc',
        borderRadius: 8,
        padding: 4,
        backgroundColor: nodeBackgroundColor,
        width: 140,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
      },
    }))

    const initialEdges: Edge[] = commits
      .filter((c) => c.parent_id)
      .map((c) => ({
        id: `${c.parent_id}->${c.commit_id}`,
        source: c.parent_id!,
        target: c.commit_id,
        animated: true,
        type: 'beizer',
        style: { stroke: '#888' },
      }))

    setNodes(initialNodes)
    setEdges(initialEdges)
  }, [commits, commitHead])

  // Highlight selected commit
  useEffect(() => {
    if (!selectedCommit) return

    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === selectedCommit.commit_id) {
          return {
            ...node,
            style: {
              ...node.style,
              borderColor: 'blue',
              backgroundColor: selectedNodeBackgroundColor,
            },
          }
        }
        return {
          ...node,
          style: {
            ...node.style,
            borderColor: node.id === commitHead?.commit_id ? 'red' : '#ccc',
            backgroundColor: nodeBackgroundColor,
          },
        }
      })
    )
  }, [selectedCommit, commitHead])

  return (
    <ReactFlowProvider>
      <div style={{ width: '100%', height: '100%', overflow: 'auto' }}>
        <ReactFlowProvider>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView={false}
            panOnScroll
            zoomOnScroll
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
        </ReactFlowProvider>
      </div>
    </ReactFlowProvider>
  )
}

export default CommitDAG