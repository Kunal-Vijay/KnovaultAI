import { describe, expect, it } from 'vitest'
import { decodeJwt } from './auth'

describe('decodeJwt', () => {
  it('returns null for invalid token', () => {
    expect(decodeJwt('not-a-jwt')).toBeNull()
  })
})
