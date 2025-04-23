/**
 * @jest-environment node
 */

import { POST, OPTIONS } from '../route';
import { writeFile } from 'fs/promises';
import { join } from 'path';

// Setup test environment
beforeAll(() => {
  // Mock global Response
  global.Response = class Response {
    status: number;
    headers: Headers;
    body: any;

    constructor(body?: any, init?: ResponseInit) {
      this.status = init?.status || 200;
      this.headers = new Headers(init?.headers);
      this.body = body;
    }
  } as any;

  // Mock global Headers
  global.Headers = class Headers {
    private headers: Map<string, string>;

    constructor(init?: any) {
      this.headers = new Map();
      if (init) {
        Object.entries(init).forEach(([key, value]) => {
          this.headers.set(key.toLowerCase(), value as string);
        });
      }
    }

    get(name: string): string | null {
      return this.headers.get(name.toLowerCase()) || null;
    }

    set(name: string, value: string): void {
      this.headers.set(name.toLowerCase(), value);
    }
  } as any;

  // Mock global Blob
  global.Blob = class Blob {
    size: number;
    type: string;
    name?: string;

    constructor(bits: any[], options?: BlobPropertyBag) {
      this.size = bits.reduce((acc, bit) => acc + (bit.length || 0), 0);
      this.type = options?.type || '';
    }

    arrayBuffer(): Promise<ArrayBuffer> {
      return Promise.resolve(new ArrayBuffer(this.size));
    }
  } as any;

  // Mock global FormData
  global.FormData = class FormData {
    private data: Map<string, any>;

    constructor() {
      this.data = new Map();
    }

    append(name: string, value: any): void {
      this.data.set(name, value);
    }

    get(name: string): any {
      return this.data.get(name);
    }
  } as any;
});

// Mock NextResponse
jest.mock('next/server', () => {
  const actualHeaders = new Headers();
  return {
    NextResponse: {
      json: jest.fn((data, options) => {
        const headers = new Headers(options?.headers);
        return {
          json: () => Promise.resolve(data),
          status: options?.status || 200,
          headers,
        };
      }),
    },
  };
});

// Mock fs/promises
jest.mock('fs/promises', () => ({
  writeFile: jest.fn(),
}));

// Mock uuid
jest.mock('uuid', () => ({
  v4: () => 'test-uuid',
}));

// Mock process.cwd
jest.mock('process', () => ({
  cwd: () => process.cwd(),
}));

describe('Upload Route', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('handles successful file upload', async () => {
    const mockFile = new Blob(['test content'], { type: 'application/x-spss-sav' }) as any;
    mockFile.name = 'test.sav';
    
    const mockFormData = new FormData();
    mockFormData.append('file', mockFile);

    const mockRequest = {
      formData: () => Promise.resolve(mockFormData),
    } as Request;

    (writeFile as jest.Mock).mockResolvedValue(undefined);

    const response = await POST(mockRequest);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data).toEqual({
      success: true,
      fileId: 'test-uuid',
      fileName: 'test.sav',
      size: mockFile.size,
    });

    expect(writeFile).toHaveBeenCalledWith(
      join(process.cwd(), 'uploads', 'test-uuid.sav'),
      expect.any(Buffer)
    );
  });

  it('returns error when no file is provided', async () => {
    const mockFormData = new FormData();
    const mockRequest = {
      formData: () => Promise.resolve(mockFormData),
    } as Request;

    const response = await POST(mockRequest);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data).toEqual({
      error: 'No file provided',
    });
  });

  it('returns error for invalid file type', async () => {
    const mockFile = new Blob(['test content'], { type: 'text/plain' }) as any;
    mockFile.name = 'test.txt';
    
    const mockFormData = new FormData();
    mockFormData.append('file', mockFile);

    const mockRequest = {
      formData: () => Promise.resolve(mockFormData),
    } as Request;

    const response = await POST(mockRequest);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data).toEqual({
      error: 'Invalid file type. Only .sav files are supported',
    });
  });

  it('returns error for oversized file', async () => {
    const largeContent = new Uint8Array(11 * 1024 * 1024);
    const mockFile = new Blob([largeContent], { type: 'application/x-spss-sav' }) as any;
    mockFile.name = 'large.sav';
    mockFile.size = 11 * 1024 * 1024;
    
    const mockFormData = new FormData();
    mockFormData.append('file', mockFile);

    const mockRequest = {
      formData: () => Promise.resolve(mockFormData),
    } as Request;

    const response = await POST(mockRequest);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data).toEqual({
      error: 'File size exceeds the maximum limit of 10MB',
    });
  });

  it('handles server errors', async () => {
    const mockFile = new Blob(['test content'], { type: 'application/x-spss-sav' }) as any;
    mockFile.name = 'test.sav';
    
    const mockFormData = new FormData();
    mockFormData.append('file', mockFile);

    const mockRequest = {
      formData: () => Promise.resolve(mockFormData),
    } as Request;

    (writeFile as jest.Mock).mockRejectedValue(new Error('Write failed'));

    const response = await POST(mockRequest);
    const data = await response.json();

    expect(response.status).toBe(500);
    expect(data).toEqual({
      error: 'Failed to upload file',
    });
  });

  it('handles OPTIONS request', async () => {
    const response = await OPTIONS();
    
    expect(response.status).toBe(204);
    expect(response.headers.get('Access-Control-Allow-Origin')).toBe('*');
    expect(response.headers.get('Access-Control-Allow-Methods')).toBe('POST, OPTIONS');
    expect(response.headers.get('Access-Control-Allow-Headers')).toBe('Content-Type');
  });
}); 