export const MIN_CLAIM_LENGTH = 3

export function normalizeClaim(text: string): string {
  return text.replace(/\r\n/g, "\n").trim()
}

export function validateClaim(text: string): { ok: true; value: string } | { ok: false; message: string } {
  const value = normalizeClaim(text)
  if (value.length < MIN_CLAIM_LENGTH) {
    return {
      ok: false,
      message: "Digite uma afirmação com pelo menos 3 caracteres.",
    }
  }
  return { ok: true, value }
}
