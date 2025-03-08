// src/tests/websocket-integration.test.js
import { testWebSocketConnection } from '../lib/utils/webSocketTester';
import { api } from '../lib/api';

/**
 * Comprehensive test suite for WebSocket and API integration
 * Run this in the browser console for best results
 */
async function runWebSocketTests() {
  console.group('🧪 Running WebSocket Integration Tests');
  const results = {
    notification: null,
    chat: null,
    api: null,
    overall: false
  };
  
  try {
    // 1. Test authentication - we need a valid token for WebSocket tests
    console.log('Testing authentication...');
    try {
      // Check if we have a valid token already
      const tokenValid = await api.auth.verifyToken().catch(e => false);
      
      if (!tokenValid) {
        console.log('No valid token found, attempting login...');
        // You'll need to provide test credentials here
        // This is just an example and should be customized for your environment
        await api.auth.login('test@example.com', 'password');
        console.log('Login successful');
      } else {
        console.log('Existing token is valid');
      }
      
      results.api = { auth: true };
    } catch (error) {
      console.error('Authentication failed:', error);
      results.api = { auth: false, error };
      throw new Error('Authentication required for WebSocket tests');
    }
    
    // 2. Get user ID for notification tests
    let userId;
    try {
      const profile = await api.profile.getProfile();
      userId = profile.id;
      console.log(`Got user ID: ${userId}`);
      results.api.userId = true;
    } catch (error) {
      console.error('Failed to get user profile:', error);
      results.api.userId = false;
      throw new Error('User ID required for WebSocket tests');
    }
    
    // 3. Test notification WebSocket
    console.log('Testing notification WebSocket connection...');
    const notificationWsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/notifications/${userId}`;
    const token = localStorage.getItem('accessToken');
    
    results.notification = await testWebSocketConnection(notificationWsUrl, {
      token,
      includeToken: true,
      timeout: 10000,
      pingMessage: { type: 'ping' },
      expectedResponse: 'pong'
    });
    
    console.log('Notification WebSocket test results:', results.notification);
    
    // 4. Test chat WebSocket with a test room
    console.log('Testing chat WebSocket connection...');
    const testRoomId = 'test-room';
    const chatWsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/chat/${testRoomId}`;
    
    results.chat = await testWebSocketConnection(chatWsUrl, {
      token,
      includeToken: true,
      timeout: 10000,
      pingMessage: { type: 'ping' },
      expectedResponse: 'pong'
    });
    
    console.log('Chat WebSocket test results:', results.chat);
    
    // 5. Test notification API
    console.log('Testing notification API...');
    try {
      const notificationsResponse = await api.notification.list();
      console.log('Notifications API response:', notificationsResponse);
      results.api.notifications = true;
    } catch (error) {
      console.error('Notification API test failed:', error);
      results.api.notifications = false;
    }
    
    // 6. Overall assessment
    results.overall = results.notification.success && 
                      results.chat.success && 
                      results.api.auth && 
                      results.api.userId && 
                      results.api.notifications;
    
    console.log(`Overall test ${results.overall ? 'PASSED ✅' : 'FAILED ❌'}`);
    
  } catch (error) {
    console.error('Test suite failed:', error);
    results.overall = false;
  }
  
  console.groupEnd();
  return results;
}

/**
 * Test notification functionality end-to-end
 */
async function testNotificationFlow() {
  console.group('🔔 Testing Notification Flow');
  const results = {
    fetchSuccess: false,
    markReadSuccess: false,
    markAllReadSuccess: false,
    deleteSuccess: false,
    overall: false
  };
  
  try {
    // 1. Fetch notifications
    console.log('Fetching notifications...');
    const notifications = await api.notification.list();
    console.log(`Found ${notifications.results?.length || 0} notifications`);
    results.fetchSuccess = true;
    
    // 2. Test marking as read (if there are unread notifications)
    const unreadNotification = notifications.results?.find(n => !n.read);
    if (unreadNotification) {
      console.log(`Testing mark as read for notification ${unreadNotification.id}...`);
      try {
        await api.notification.markAsRead(unreadNotification.id);
        console.log('Mark as read succeeded');
        results.markReadSuccess = true;
      } catch (error) {
        console.error('Mark as read failed:', error);
        results.markReadSuccess = false;
      }
    } else {
      console.log('No unread notifications to test markAsRead');
      results.markReadSuccess = 'skipped';
    }
    
    // 3. Test mark all as read
    console.log('Testing mark all as read...');
    try {
      await api.notification.markAllAsRead();
      console.log('Mark all as read succeeded');
      results.markAllReadSuccess = true;
    } catch (error) {
      console.error('Mark all as read failed:', error);
      results.markAllReadSuccess = false;
    }
    
    // 4. Test delete notification (if there are any notifications)
    if (notifications.results?.length > 0) {
      const notificationToDelete = notifications.results[0];
      console.log(`Testing delete for notification ${notificationToDelete.id}...`);
      try {
        await api.notification.delete(notificationToDelete.id);
        console.log('Delete succeeded');
        results.deleteSuccess = true;
      } catch (error) {
        console.error('Delete failed:', error);
        results.deleteSuccess = false;
      }
    } else {
      console.log('No notifications to test delete');
      results.deleteSuccess = 'skipped';
    }
    
    // 5. Overall assessment
    results.overall = results.fetchSuccess && 
                     (results.markReadSuccess === true || results.markReadSuccess === 'skipped') &&
                     results.markAllReadSuccess &&
                     (results.deleteSuccess === true || results.deleteSuccess === 'skipped');
    
    console.log(`Notification flow test ${results.overall ? 'PASSED ✅' : 'FAILED ❌'}`);
    
  } catch (error) {
    console.error('Notification flow test failed:', error);
    results.overall = false;
  }
  
  console.groupEnd();
  return results;
}

/**
 * Run all tests and display results
 */
async function runAllTests() {
  console.group('🚀 Running All Integration Tests');
  
  const wsResults = await runWebSocketTests();
  const notificationResults = await testNotificationFlow();
  
  const allPassed = wsResults.overall && notificationResults.overall;
  
  console.log(`
    ========== TEST SUMMARY ==========
    WebSocket Tests: ${wsResults.overall ? 'PASSED ✅' : 'FAILED ❌'}
    Notification Flow: ${notificationResults.overall ? 'PASSED ✅' : 'FAILED ❌'}
    ---------------------------------
    Overall: ${allPassed ? 'PASSED ✅' : 'FAILED ❌'}
  `);
  
  console.groupEnd();
  return { wsResults, notificationResults, allPassed };
}

// Expose functions for browser console testing
window.testWebSockets = runWebSocketTests;
window.testNotifications = testNotificationFlow;
window.runAllTests = runAllTests;

export {
  runWebSocketTests,
  testNotificationFlow,
  runAllTests
};