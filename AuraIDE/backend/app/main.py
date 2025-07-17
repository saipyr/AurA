from fastapi import FastAPI, HTTPException, Query, Body, WebSocket, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import os
import shutil
import asyncio
import subprocess
import uuid
import time

app = FastAPI()

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

def safe_path(path: str):
    abs_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))
    if not abs_path.startswith(PROJECT_ROOT):
        raise HTTPException(status_code=400, detail='Invalid file path')
    return abs_path

def git_run(args, cwd=PROJECT_ROOT):
    try:
        result = subprocess.run(['git'] + args, cwd=cwd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout + e.stderr

@app.get('/api/git/status')
def git_status():
    output = git_run(['status', '--porcelain'])
    files = []
    for line in output.splitlines():
        if not line.strip():
            continue
        status_code = line[:2]
        file_path = line[3:]
        if status_code[0] != ' ':
            status = 'staged'
        elif status_code[1] != ' ':
            status = 'unstaged'
        else:
            status = 'untracked'
        files.append({'path': file_path, 'status': status, 'raw': status_code})
    return {'files': files}

@app.post('/api/git/commit')
def git_commit(request: Request):
    data = asyncio.run(request.json())
    message = data.get('message', '')
    output = git_run(['commit', '-am', message])
    return {'output': output}

@app.post('/api/git/push')
def git_push():
    output = git_run(['push'])
    return {'output': output}

@app.post('/api/git/pull')
def git_pull():
    output = git_run(['pull'])
    return {'output': output}

@app.get('/api/git/branches')
def git_branches():
    output = git_run(['branch', '-a'])
    return {'branches': output}

@app.post('/api/git/checkout')
def git_checkout(request: Request):
    data = asyncio.run(request.json())
    branch = data.get('branch', '')
    output = git_run(['checkout', branch])
    return {'output': output}

@app.post('/api/git/stage')
def git_stage(request: Request):
    data = asyncio.run(request.json())
    file = data.get('file', '')
    if not file:
        raise HTTPException(status_code=400, detail='File is required')
    output = git_run(['add', file])
    return {'output': output}

@app.post('/api/git/unstage')
def git_unstage(request: Request):
    data = asyncio.run(request.json())
    file = data.get('file', '')
    if not file:
        raise HTTPException(status_code=400, detail='File is required')
    output = git_run(['reset', 'HEAD', file])
    return {'output': output}

@app.get('/api/git/diff')
def git_diff(file: str = Query(None), staged: bool = Query(False), commit: str = Query(None)):
    args = ['diff']
    if staged:
        args.append('--cached')
    if commit:
        args += [commit]
    if file:
        args += ['--', file]
    output = git_run(args)
    return {'diff': output}

@app.get('/api/git/file-content')
def git_file_content(file: str = Query(...), ref: str = Query('working')):
    import os
    abs_path = os.path.abspath(os.path.join(PROJECT_ROOT, file))
    if not abs_path.startswith(PROJECT_ROOT):
        raise HTTPException(status_code=400, detail='Invalid file path')
    if ref == 'working':
        # Return working directory content
        if not os.path.isfile(abs_path):
            return {'content': ''}
        with open(abs_path, 'r', encoding='utf-8') as f:
            return {'content': f.read()}
    elif ref == 'HEAD':
        # Return last committed version
        output = git_run(['show', f'HEAD:{file}'])
        return {'content': output}
    elif ref == 'index':
        # Return staged version
        output = git_run(['show', f':{file}'])
        return {'content': output}
    else:
        raise HTTPException(status_code=400, detail='Invalid ref')

@app.get('/api/project/settings')
def get_project_settings():
    import os, json
    settings_path = os.path.join(PROJECT_ROOT, '.aura', 'settings.json')
    if not os.path.exists(settings_path):
        return {}
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/project/settings')
def set_project_settings(request: Request):
    import os, json
    data = asyncio.run(request.json())
    settings_dir = os.path.join(PROJECT_ROOT, '.aura')
    os.makedirs(settings_dir, exist_ok=True)
    settings_path = os.path.join(settings_dir, 'settings.json')
    try:
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/files/read', response_class=PlainTextResponse)
def read_file(path: str = Query(...)):
    abs_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))
    if not abs_path.startswith(PROJECT_ROOT):
        raise HTTPException(status_code=400, detail='Invalid file path')
    if not os.path.isfile(abs_path):
        raise HTTPException(status_code=404, detail='File not found')
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/files/save')
def save_file(path: str = Query(...), content: str = Body(...)):
    abs_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))
    if not abs_path.startswith(PROJECT_ROOT):
        raise HTTPException(status_code=400, detail='Invalid file path')
    try:
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/files/list', response_class=JSONResponse)
def list_dir(path: str = Query('')):
    abs_path = safe_path(path)
    if not os.path.isdir(abs_path):
        raise HTTPException(status_code=404, detail='Directory not found')
    try:
        items = []
        for name in os.listdir(abs_path):
            full = os.path.join(abs_path, name)
            items.append({
                'name': name,
                'isDir': os.path.isdir(full)
            })
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/files/create_file')
def create_file(path: str = Query(...)):
    abs_path = safe_path(path)
    if os.path.exists(abs_path):
        raise HTTPException(status_code=400, detail='File already exists')
    try:
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write('')
        return {"status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/files/create_folder')
def create_folder(path: str = Query(...)):
    abs_path = safe_path(path)
    if os.path.exists(abs_path):
        raise HTTPException(status_code=400, detail='Folder already exists')
    try:
        os.makedirs(abs_path)
        return {"status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/files/rename')
def rename_path(old_path: str = Query(...), new_path: str = Query(...)):
    abs_old = safe_path(old_path)
    abs_new = safe_path(new_path)
    if not os.path.exists(abs_old):
        raise HTTPException(status_code=404, detail='Source not found')
    if os.path.exists(abs_new):
        raise HTTPException(status_code=400, detail='Target already exists')
    try:
        os.rename(abs_old, abs_new)
        return {"status": "renamed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/files/delete')
def delete_path(path: str = Query(...)):
    abs_path = safe_path(path)
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail='Path not found')
    try:
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        else:
            os.remove(abs_path)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

LSP_SERVERS = {
    'python': ['pyright-langserver', '--stdio'],
    'typescript': ['typescript-language-server', '--stdio'],
    'javascript': ['typescript-language-server', '--stdio'],
    # Add more language servers as needed
}

@app.websocket('/ws/lsp')
async def lsp_ws(websocket: WebSocket, language: str = Query(...)):
    await websocket.accept()
    if language not in LSP_SERVERS:
        await websocket.close(code=4000)
        return
    proc = await asyncio.create_subprocess_exec(
        *LSP_SERVERS[language],
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE
    )
    async def ws_to_proc():
        try:
            while True:
                data = await websocket.receive_bytes()
                proc.stdin.write(data)
                await proc.stdin.drain()
        except Exception:
            pass
    async def proc_to_ws():
        try:
            while True:
                data = await proc.stdout.read(4096)
                if not data:
                    break
                await websocket.send_bytes(data)
        except Exception:
            pass
    await asyncio.gather(ws_to_proc(), proc_to_ws())
    proc.terminate()
    await proc.wait()

TERMINAL_SESSIONS = {}
SESSION_TIMEOUT = 300  # seconds

async def cleanup_sessions():
    while True:
        now = time.time()
        to_delete = []
        for sid, sess in list(TERMINAL_SESSIONS.items()):
            if now - sess['last_access'] > SESSION_TIMEOUT:
                proc = sess['proc']
                proc.terminate()
                await proc.wait()
                to_delete.append(sid)
        for sid in to_delete:
            del TERMINAL_SESSIONS[sid]
        await asyncio.sleep(60)

@app.on_event('startup')
async def start_cleanup():
    asyncio.create_task(cleanup_sessions())

@app.websocket('/ws/terminal')
async def terminal_ws(websocket: WebSocket, session: str = Query(None)):
    await websocket.accept()
    if not session:
        session = str(uuid.uuid4())
    now = time.time()
    if session in TERMINAL_SESSIONS:
        sess = TERMINAL_SESSIONS[session]
        proc = sess['proc']
        sess['last_access'] = now
    else:
        shell = os.environ.get('SHELL', '/bin/bash')
        proc = await asyncio.create_subprocess_exec(
            shell,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        TERMINAL_SESSIONS[session] = {'proc': proc, 'last_access': now}
    async def ws_to_proc():
        try:
            while True:
                data = await websocket.receive_text()
                proc.stdin.write(data.encode())
                await proc.stdin.drain()
                TERMINAL_SESSIONS[session]['last_access'] = time.time()
        except Exception:
            pass
    async def proc_to_ws():
        try:
            while True:
                data = await proc.stdout.read(1024)
                if not data:
                    break
                await websocket.send_text(data.decode(errors='ignore'))
                TERMINAL_SESSIONS[session]['last_access'] = time.time()
        except Exception:
            pass
    await asyncio.gather(ws_to_proc(), proc_to_ws())
    # Do not terminate proc here; cleanup task will handle it 