/**
 * Integration Example Component
 * Shows how to integrate PlatformPersonaChat into existing editors
 * Demonstrates practical usage patterns for different platforms
 */

import React from 'react';
import { PlatformPersonaProvider } from '../PersonaContext';
import { PlatformPersonaChat } from './PlatformPersonaChat';
import { PlatformType } from '../../../types/PlatformPersonaTypes';

// Example: LinkedIn Writer Integration
export const LinkedInWriterWithPersonaChat: React.FC = () => {
  return (
    <div className="linkedin-writer-container">
      {/* Existing LinkedIn Editor Content */}
      <div className="linkedin-editor-section p-4 border rounded-lg mb-4">
        <h3 className="text-lg font-semibold mb-3">LinkedIn Content Editor</h3>
        <textarea
          className="w-full p-3 border rounded-lg"
          rows={6}
          placeholder="Write your LinkedIn post here..."
        />
        <div className="mt-3 flex gap-2">
          <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Preview
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
            Schedule
          </button>
        </div>
      </div>

      {/* Persona-Aware Chat Integration */}
      <div className="persona-chat-section">
        <h3 className="text-lg font-semibold mb-3">AI Content Assistant</h3>
        <PlatformPersonaProvider platform="linkedin">
          <PlatformPersonaChat
            platform="linkedin"
            showWelcomeMessage={true}
            showSuggestedPrompts={true}
            className="border rounded-lg"
          />
        </PlatformPersonaProvider>
      </div>
    </div>
  );
};

// Example: Facebook Writer Integration
export const FacebookWriterWithPersonaChat: React.FC = () => {
  return (
    <div className="facebook-writer-container">
      {/* Existing Facebook Editor Content */}
      <div className="facebook-editor-section p-4 border rounded-lg mb-4">
        <h3 className="text-lg font-semibold mb-3">Facebook Content Editor</h3>
        <textarea
          className="w-full p-3 border rounded-lg"
          rows={4}
          placeholder="Write your Facebook post here..."
        />
        <div className="mt-3 flex gap-2">
          <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Preview
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
            Schedule
          </button>
        </div>
      </div>

      {/* Persona-Aware Chat Integration */}
      <div className="persona-chat-section">
        <h3 className="text-lg font-semibold mb-3">AI Content Assistant</h3>
        <PlatformPersonaProvider platform="facebook">
          <PlatformPersonaChat
            platform="facebook"
            showWelcomeMessage={true}
            showSuggestedPrompts={true}
            className="border rounded-lg"
          />
        </PlatformPersonaProvider>
      </div>
    </div>
  );
};

// Example: Instagram Writer Integration
export const InstagramWriterWithPersonaChat: React.FC = () => {
  return (
    <div className="instagram-writer-container">
      {/* Existing Instagram Editor Content */}
      <div className="instagram-editor-section p-4 border rounded-lg mb-4">
        <h3 className="text-lg font-semibold mb-3">Instagram Content Editor</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-3">
              <p className="text-gray-500">Upload Image/Video</p>
            </div>
            <textarea
              className="w-full p-3 border rounded-lg"
              rows={4}
              placeholder="Write your Instagram caption here..."
            />
          </div>
          <div>
            <h4 className="font-medium mb-2">Hashtag Suggestions</h4>
            <div className="space-y-2">
              <div className="flex flex-wrap gap-1">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">#content</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">#strategy</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">#growth</span>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-3 flex gap-2">
          <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Preview
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
            Schedule
          </button>
        </div>
      </div>

      {/* Persona-Aware Chat Integration */}
      <div className="persona-chat-section">
        <h3 className="text-lg font-semibold mb-3">AI Content Assistant</h3>
        <PlatformPersonaProvider platform="instagram">
          <PlatformPersonaChat
            platform="instagram"
            showWelcomeMessage={true}
            showSuggestedPrompts={true}
            className="border rounded-lg"
          />
        </PlatformPersonaProvider>
      </div>
    </div>
  );
};

// Main integration example component
export const IntegrationExample: React.FC = () => {
  const [selectedPlatform, setSelectedPlatform] = React.useState<PlatformType>('linkedin');

  const renderSelectedEditor = () => {
    switch (selectedPlatform) {
      case 'linkedin':
        return <LinkedInWriterWithPersonaChat />;
      case 'facebook':
        return <FacebookWriterWithPersonaChat />;
      case 'instagram':
        return <InstagramWriterWithPersonaChat />;
      default:
        return <LinkedInWriterWithPersonaChat />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Platform Persona Chat Integration Examples
        </h1>
        <p className="text-gray-600">
          See how to integrate persona-aware AI chat into existing content editors
        </p>
      </div>

      {/* Platform Tabs */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        {(['linkedin', 'facebook', 'instagram'] as PlatformType[]).map((platform) => (
          <button
            key={platform}
            onClick={() => setSelectedPlatform(platform)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedPlatform === platform
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {platform.charAt(0).toUpperCase() + platform.slice(1)}
          </button>
        ))}
      </div>

      {/* Selected Editor */}
      {renderSelectedEditor()}

      {/* Integration Benefits */}
      <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Benefits of Persona-Aware Chat Integration
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">🎯 Personalized Assistance</h4>
            <p className="text-sm text-gray-700">
              AI responses automatically match your writing style, vocabulary preferences, and brand voice
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">🚀 Platform Optimization</h4>
            <p className="text-sm text-gray-700">
              Get platform-specific advice for character limits, hashtag strategies, and engagement patterns
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">💡 Contextual Intelligence</h4>
            <p className="text-sm text-gray-700">
              AI understands your content goals, audience, and industry context for better suggestions
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">⚡ Seamless Workflow</h4>
            <p className="text-sm text-gray-700">
              Chat directly in your editor while maintaining focus on content creation
            </p>
          </div>
        </div>
      </div>

      {/* Implementation Notes */}
      <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">Implementation Notes</h4>
        <div className="text-sm text-gray-700 space-y-2">
          <p>
            <strong>1. Wrap your editor with PlatformPersonaProvider:</strong> This provides persona context to all child components.
          </p>
          <p>
            <strong>2. Add PlatformPersonaChat component:</strong> Place it where you want the AI chat interface.
          </p>
          <p>
            <strong>3. Configure platform-specific settings:</strong> The chat automatically adapts to each platform's requirements.
          </p>
          <p>
            <strong>4. Customize appearance:</strong> Use className and other props to match your editor's design.
          </p>
        </div>
      </div>
    </div>
  );
};

export default IntegrationExample;
