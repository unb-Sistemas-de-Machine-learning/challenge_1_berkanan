const PREFIX = "berkanan."

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined"
}

export function storageGet(key: string): string | null {
  if (!canUseStorage()) return null
  try {
    return window.localStorage.getItem(`${PREFIX}${key}`)
  } catch {
    return null
  }
}

export function storageSet(key: string, value: string): void {
  if (!canUseStorage()) return
  try {
    window.localStorage.setItem(`${PREFIX}${key}`, value)
  } catch {
    // Storage may be blocked in private mode.
  }
}

export function storageRemove(key: string): void {
  if (!canUseStorage()) return
  try {
    window.localStorage.removeItem(`${PREFIX}${key}`)
  } catch {
    // ignore
  }
}

export function storageGetJson<T>(key: string, fallback: T): T {
  const raw = storageGet(key)
  if (!raw) return fallback
  try {
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

export function storageSetJson(key: string, value: unknown): void {
  storageSet(key, JSON.stringify(value))
}
