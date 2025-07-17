export async function gitStatus(): Promise<any> {
  const res = await fetch('/api/git/status');
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.files;
}

export async function gitCommit(message: string): Promise<string> {
  const res = await fetch('/api/git/commit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.output;
}

export async function gitPush(): Promise<string> {
  const res = await fetch('/api/git/push', { method: 'POST' });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.output;
}

export async function gitPull(): Promise<string> {
  const res = await fetch('/api/git/pull', { method: 'POST' });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.output;
}

export async function gitBranches(): Promise<string> {
  const res = await fetch('/api/git/branches');
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.branches;
}

export async function gitCheckout(branch: string): Promise<string> {
  const res = await fetch('/api/git/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ branch }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.output;
}

export async function gitStage(file: string): Promise<string> {
  const res = await fetch('/api/git/stage', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.output;
}

export async function gitUnstage(file: string): Promise<string> {
  const res = await fetch('/api/git/unstage', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.output;
}

export async function gitDiff(file?: string, staged?: boolean, commit?: string): Promise<string> {
  let url = '/api/git/diff';
  const params = [];
  if (file) params.push(`file=${encodeURIComponent(file)}`);
  if (staged) params.push('staged=true');
  if (commit) params.push(`commit=${encodeURIComponent(commit)}`);
  if (params.length) url += '?' + params.join('&');
  const res = await fetch(url);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.diff;
}

export async function gitFileContent(file: string, ref: 'working' | 'HEAD' | 'index' = 'working'): Promise<string> {
  const url = `/api/git/file-content?file=${encodeURIComponent(file)}&ref=${ref}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.content;
} 