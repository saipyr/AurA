// NOTE: Ensure your tsconfig.json includes "lib": ["ES2015"] for Promise support.

export async function readFile(path: string): Promise<string> {
  const res = await fetch(`/api/files/read?path=${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error(await res.text());
  return await res.text();
}

export async function saveFile(path: string, content: string): Promise<void> {
  const res = await fetch(`/api/files/save?path=${encodeURIComponent(path)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'text/plain' },
    body: content,
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function listDir(path: string = ''): Promise<Array<{name: string, isDir: boolean}>> {
  const res = await fetch(`/api/files/list?path=${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

export async function createFile(path: string): Promise<void> {
  const res = await fetch(`/api/files/create_file?path=${encodeURIComponent(path)}`, { method: 'POST' });
  if (!res.ok) throw new Error(await res.text());
}

export async function createFolder(path: string): Promise<void> {
  const res = await fetch(`/api/files/create_folder?path=${encodeURIComponent(path)}`, { method: 'POST' });
  if (!res.ok) throw new Error(await res.text());
}

export async function renamePath(oldPath: string, newPath: string): Promise<void> {
  const res = await fetch(`/api/files/rename?old_path=${encodeURIComponent(oldPath)}&new_path=${encodeURIComponent(newPath)}`, { method: 'POST' });
  if (!res.ok) throw new Error(await res.text());
}

export async function deletePath(path: string): Promise<void> {
  const res = await fetch(`/api/files/delete?path=${encodeURIComponent(path)}`, { method: 'POST' });
  if (!res.ok) throw new Error(await res.text());
}

export default { readFile, saveFile, listDir, createFile, createFolder, renamePath, deletePath }; 