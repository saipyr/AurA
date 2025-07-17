import { render, fireEvent } from '@testing-library/svelte';
import FileExplorer from './FileExplorer.svelte';

jest.mock('../apis/files/index', () => ({
  listDir: jest.fn(() => Promise.resolve([
    { name: 'file1.txt', isDir: false },
    { name: 'folder1', isDir: true }
  ])),
  createFile: jest.fn(() => Promise.resolve()),
  createFolder: jest.fn(() => Promise.resolve()),
  renamePath: jest.fn(() => Promise.resolve()),
  deletePath: jest.fn(() => Promise.resolve()),
}));

describe('FileExplorer', () => {
  it('renders files and folders and emits open event', async () => {
    const { getByText, component } = render(FileExplorer);
    expect(getByText('file1.txt')).toBeInTheDocument();
    expect(getByText('folder1')).toBeInTheDocument();
    const openHandler = jest.fn();
    component.$on('open', openHandler);
    await fireEvent.click(getByText('file1.txt'));
    expect(openHandler).toHaveBeenCalled();
  });
}); 