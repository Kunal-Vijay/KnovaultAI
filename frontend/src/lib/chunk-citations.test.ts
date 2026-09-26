import { describe, expect, it } from 'vitest'
import { chunkIndexFromHref, linkifyChunkReferences } from './chunk-citations'

describe('linkifyChunkReferences', () => {
  it('linkifies a single chunk reference', () => {
    expect(linkifyChunkReferences('See [Chunk 1] for details.')).toBe(
      'See [Chunk 1](#chunk-1) for details.',
    )
  })

  it('linkifies comma-separated chunk groups', () => {
    expect(linkifyChunkReferences('text [Chunk 3, Chunk 7] end')).toBe(
      'text [Chunk 3](#chunk-3) [Chunk 7](#chunk-7) end',
    )
  })

  it('leaves text without chunk brackets unchanged', () => {
    const plain = 'Tokenization splits text into tokens.'
    expect(linkifyChunkReferences(plain)).toBe(plain)
  })

  it('handles mixed sentence from RAG answers', () => {
    const input =
      'processing [Chunk 3, Chunk 7]. vocabulary [Chunk 3]. char [Chunk 1].'
    expect(linkifyChunkReferences(input)).toBe(
      'processing [Chunk 3](#chunk-3) [Chunk 7](#chunk-7). vocabulary [Chunk 3](#chunk-3). char [Chunk 1](#chunk-1).',
    )
  })
})

describe('chunkIndexFromHref', () => {
  it('parses chunk fragment', () => {
    expect(chunkIndexFromHref('#chunk-5')).toBe(5)
    expect(chunkIndexFromHref('https://example.com')).toBeNull()
  })
})
