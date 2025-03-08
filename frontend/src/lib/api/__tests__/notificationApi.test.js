// /src/lib/api/__tests__/notificationApi.test.js
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest';
import { notificationApi } from '../notificationApi';

// Mock the fetch function
global.fetch = vi.fn();
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn()
};

// Helper to mock fetch responses
function mockFetchResponse(data, options = {}) {
  const response = {
    ok: options.ok !== false,
    status: options.status || 200,
    statusText: options.statusText || 'OK',
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    headers: {
      get: (header) => {
        if (header === 'content-type') {
          return 'application/json';
        }
        return null;
      }
    }
  };
  global.fetch.mockResolvedValueOnce(response);
  return response;
}

describe('Notification API', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
    global.localStorage.getItem.mockReturnValue('fake-token');
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  test('list should fetch notifications with correct endpoint', async () => {
    const mockData = {
      success: true,
      results: [
        { id: '1', title: 'Test Notification', read: false }
      ]
    };
    mockFetchResponse(mockData);

    const result = await notificationApi.list();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/base/notifications/'),
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json'
        })
      })
    );
    expect(result).toEqual(mockData);
  });

  test('markAsRead should call correct endpoint with notification ID', async () => {
    const mockData = { success: true };
    mockFetchResponse(mockData);

    const result = await notificationApi.markAsRead('123');

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/base/notifications/123/read/'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json'
        })
      })
    );
    expect(result).toEqual(mockData);
  });

  test('markAllAsRead should call the correct endpoint', async () => {
    const mockData = { success: true };
    mockFetchResponse(mockData);

    const result = await notificationApi.markAllAsRead();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/base/notifications/read-all/'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json'
        })
      })
    );
    expect(result).toEqual(mockData);
  });

  test('delete should call the correct endpoint with notification ID', async () => {
    const mockData = { success: true };
    mockFetchResponse(mockData);

    const result = await notificationApi.delete('123');

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/base/notifications/123/'),
      expect.objectContaining({
        method: 'DELETE',
        headers: expect.objectContaining({
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json'
        })
      })
    );
    expect(result).toEqual(mockData);
  });

  test('getSettings should call the correct endpoint', async () => {
    const mockData = { 
      success: true,
      settings: { 
        email_notifications: true,
        push_notifications: false 
      }
    };
    mockFetchResponse(mockData);

    const result = await notificationApi.getSettings();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/base/notifications/settings/'),
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json'
        })
      })
    );
    expect(result).toEqual(mockData);
  });

  test('updateSettings should call the correct endpoint with settings data', async () => {
    const mockData = { success: true };
    mockFetchResponse(mockData);
    
    const settings = {
      email_notifications: true,
      push_notifications: true
    };

    const result = await notificationApi.updateSettings(settings);

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/base/notifications/settings/'),
      expect.objectContaining({
        method: 'PUT',
        headers: expect.objectContaining({
          'Authorization': 'Bearer fake-token',
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify(settings)
      })
    );
    expect(result).toEqual(mockData);
  });

  test('should handle error responses correctly', async () => {
    const errorData = {
      error: 'Something went wrong',
      code: 'server_error'
    };
    mockFetchResponse(errorData, { ok: false, status: 500, statusText: 'Internal Server Error' });

    await expect(notificationApi.list()).rejects.toMatchObject({
      status: 500,
      error: 'Something went wrong',
      code: 'server_error'
    });
  });

  test('should handle network errors correctly', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    await expect(notificationApi.list()).rejects.toMatchObject({
      status: 0,
      error: expect.stringContaining('Network error'),
      code: 'network_error'
    });
  });
});