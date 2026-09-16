const BASE = (import.meta.env.VITE_API_URL ?? "http://localhost:8000") + "/api/v1";

export interface ApiError {
  status: number;
  detail: string;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    ...init,
    headers: { "content-type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* ignore */
    }
    throw { status: res.status, detail } as ApiError;
  }
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(p: string) => req<T>(p),
  post: <T>(p: string, body: unknown) =>
    req<T>(p, { method: "POST", body: JSON.stringify(body) }),
  postForm: async (p: string, form: FormData) => {
    const res = await fetch(BASE + p, { method: "POST", body: form });
    if (!res.ok) throw { status: res.status, detail: await res.text() } as ApiError;
    return res.json();
  },
  // devolve um blob (PDF)
  postBlob: async (p: string, body: unknown) => {
    const res = await fetch(BASE + p, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw { status: res.status, detail: await res.text() } as ApiError;
    return res.blob();
  },
};
