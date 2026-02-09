/**
 * Utility to test and debug CopilotKit persistence
 */

import { STORAGE_KEYS } from './enhancedPersistence';

export const testPersistence = () => {
  console.log('🧪 Testing CopilotKit persistence...');
  
  // Check localStorage for persisted data
  const chatData = localStorage.getItem(STORAGE_KEYS.CHAT_HISTORY);
  const prefsData = localStorage.getItem(STORAGE_KEYS.USER_PREFERENCES);
  const contextData = localStorage.getItem(STORAGE_KEYS.CONVERSATION_CONTEXT);
  
  console.log('📊 Persistence Test Results:', {
    chat: {
      exists: !!chatData,
      length: chatData ? JSON.parse(chatData).length : 0,
      sample: chatData ? JSON.parse(chatData).slice(0, 2) : null
    },
    preferences: {
      exists: !!prefsData,
      data: prefsData ? JSON.parse(prefsData) : null
    },
    context: {
      exists: !!contextData,
      data: contextData ? JSON.parse(contextData) : null
    }
  });
  
  // Check for any other CopilotKit related data
  const allKeys = Object.keys(localStorage);
  const copilotKeys = allKeys.filter(key => key.includes('copilot') || key.includes('alwrity'));
  
  console.log('🔍 All CopilotKit related localStorage keys:', copilotKeys);
  
  return {
    chat: !!chatData,
    preferences: !!prefsData,
    context: !!contextData,
    allCopilotKeys: copilotKeys
  };
};

export const clearPersistence = () => {
  console.log('🗑️ Clearing CopilotKit persistence...');
  
  Object.values(STORAGE_KEYS).forEach((key) => {
    localStorage.removeItem(key);
  });
  
  // Clear any other CopilotKit related data
  const allKeys = Object.keys(localStorage);
  const copilotKeys = allKeys.filter(key => key.includes('copilot') || key.includes('alwrity'));
  
  copilotKeys.forEach(key => {
    localStorage.removeItem(key);
    console.log(`🗑️ Removed: ${key}`);
  });
  
  console.log('✅ Persistence cleared');
};

export const simulateChatMessage = () => {
  console.log('💬 Simulating chat message for persistence test...');
  
  const testMessage = {
    role: 'user',
    content: 'This is a test message to verify persistence',
    timestamp: Date.now(),
    id: `test-${Date.now()}`
  };
  
  // Try to store in the expected format
  try {
    const existingChat = localStorage.getItem(STORAGE_KEYS.CHAT_HISTORY);
    const chatArray = existingChat ? JSON.parse(existingChat) : [];
    chatArray.push(testMessage);
    
    // Keep only last 10 messages for testing
    const trimmedChat = chatArray.slice(-10);
    localStorage.setItem(STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(trimmedChat));
    
    console.log('✅ Test message stored:', testMessage);
    return true;
  } catch (error) {
    console.error('❌ Failed to store test message:', error);
    return false;
  }
};
