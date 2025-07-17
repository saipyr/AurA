import { render, fireEvent } from '@testing-library/svelte';
import MonacoEditor from './MonacoEditor.svelte';

jest.mock('../apis/files/index', () => ({
  readFile: jest.fn(() => Promise.resolve('test content')),
  saveFile: jest.fn(() => Promise.resolve()),
}));

// Mock monaco-editor
jest.mock('monaco-editor', () => ({
  editor: {
    create: jest.fn((container, opts) => {
      let value = opts.value || '';
      return {
        setValue: (v) => { value = v; },
        getValue: () => value,
        onDidChangeModelContent: (cb) => {},
      };
    })
  }
}));

describe('MonacoEditor', () => {
  it('loads and displays file content', async () => {
    const { getByLabelText } = render(MonacoEditor, { filePath: 'test.txt', language: 'javascript', theme: 'vs-dark' });
    expect(getByLabelText('Editing: test.txt')).toBeInTheDocument();
  });
}); 