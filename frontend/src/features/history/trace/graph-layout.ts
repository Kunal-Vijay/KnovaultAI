import type { SpanTreeNode } from '@/types/history'
import { spanKey } from '@/features/history/trace/trace-tree'

export type LaidOutNode = {
  id: string
  x: number
  y: number
  width: number
  height: number
}

const NODE_WIDTH = 188
const NODE_HEIGHT = 58
const H_GAP = 28
const V_GAP = 72

export function layoutSpanForest(
  roots: SpanTreeNode[],
  opts?: { nodeWidth?: number; nodeHeight?: number; hGap?: number; vGap?: number },
): Map<string, LaidOutNode> {
  const nodeWidth = opts?.nodeWidth ?? NODE_WIDTH
  const nodeHeight = opts?.nodeHeight ?? NODE_HEIGHT
  const hGap = opts?.hGap ?? H_GAP
  const vGap = opts?.vGap ?? V_GAP

  const positions = new Map<string, LaidOutNode>()

  function subtreeWidth(node: SpanTreeNode): number {
    if (node.children.length === 0) return nodeWidth
    const childrenW = node.children.reduce(
      (sum, child, i) => sum + subtreeWidth(child) + (i > 0 ? hGap : 0),
      0,
    )
    return Math.max(nodeWidth, childrenW)
  }

  function place(node: SpanTreeNode, left: number, depth: number) {
    const width = subtreeWidth(node)
    const x = left + width / 2 - nodeWidth / 2
    const y = depth * (nodeHeight + vGap)

    positions.set(spanKey(node), {
      id: spanKey(node),
      x,
      y,
      width: nodeWidth,
      height: nodeHeight,
    })

    if (node.children.length === 0) return

    const childrenW = node.children.reduce(
      (sum, child, i) => sum + subtreeWidth(child) + (i > 0 ? hGap : 0),
      0,
    )
    let cursor = left + (width - childrenW) / 2
    for (const child of node.children) {
      const w = subtreeWidth(child)
      place(child, cursor, depth + 1)
      cursor += w + hGap
    }
  }

  let cursor = 0
  for (const root of roots) {
    const w = subtreeWidth(root)
    place(root, cursor, 0)
    cursor += w + hGap * 2
  }

  return positions
}

export const GRAPH_NODE_SIZE = {
  width: NODE_WIDTH,
  height: NODE_HEIGHT,
} as const
