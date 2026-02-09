import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider
} from '@mui/material';
import { apiClient } from '../../api/client';
import { createClient, OAuthStrategy } from '@wix/sdk';
import { apiClient } from '../../api/client';
import { categories as blogCategoriesModule, tags as blogTagsModule } from '@wix/blog';

interface WixConnectionStatus {
  connected: boolean;
  has_permissions: boolean;
  site_info?: any;
  permissions?: any;
  error?: string;
}

interface BlogCategories {
  categories: Array<{
    id: string;
    name: string;
    description?: string;
  }>;
}

interface BlogTags {
  tags: Array<{
    id: string;
    label: string;
  }>;
}

const WixTestPage: React.FC = () => {
  const [connectionStatus, setConnectionStatus] = useState<WixConnectionStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [categories, setCategories] = useState<BlogCategories | null>(null);
  const [tags, setTags] = useState<BlogTags | null>(null);
  
  // Blog post form state
  const [blogTitle, setBlogTitle] = useState('Test Blog Post from ALwrity');
  const [blogContent, setBlogContent] = useState(`# Welcome to ALwrity-Wix Integration!

This is a test blog post created from the ALwrity platform and published directly to your Wix website.

## Features

- **Seamless Integration**: Publish directly from ALwrity to Wix
- **Rich Content**: Support for headings, paragraphs, and formatting
- **Image Support**: Automatic image import to Wix Media Manager
- **Category & Tag Support**: Organize your content with Wix categories and tags

## How It Works

1. Connect your Wix account to ALwrity
2. Generate your blog content using ALwrity's AI tools
3. Click "Publish to Wix" to publish directly to your website
4. Your content appears on your Wix blog instantly!

## Next Steps

This integration opens up new possibilities for content creators who want to leverage ALwrity's AI-powered writing tools while maintaining their Wix website presence.

*Published from ALwrity on ${new Date().toLocaleDateString()}*`);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [coverImageUrl, setCoverImageUrl] = useState('');

  // Check connection status on component mount
  useEffect(() => {
    checkConnectionStatus();
  }, []);

  const checkConnectionStatus = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/wix/test/connection/status');
      const connectedFlag = sessionStorage.getItem('wix_connected') === 'true';
      setConnectionStatus({
        ...response.data,
        connected: connectedFlag || response.data.connected,
      });
    } catch (error) {
      console.error('Failed to check connection status:', error);
      setConnectionStatus({
        connected: false,
        has_permissions: false,
        error: 'Failed to check connection status'
      });
    } finally {
      setLoading(false);
    }
  };

  const getAuthorizationUrl = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/oauth/wix/auth-url');
      const { url: authUrl, details } = response.data;
      const oauthData = details?.oauth_data;
      const clientId = details?.client_id;
      if (!authUrl || !oauthData) {
        throw new Error('Missing Wix OAuth configuration from backend.');
      }
      if (clientId) {
        const wixClient = createClient({ auth: OAuthStrategy({ clientId }) });
        wixClient.auth.setTokens({});
      }
      // Use sessionStorage to ensure data is scoped to this tab/session
      sessionStorage.setItem('wix_oauth_data', JSON.stringify(oauthData));
      window.location.href = authUrl;
    } catch (error) {
      console.error('Failed to start Wix OAuth flow:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const tokensRaw = sessionStorage.getItem('wix_tokens');
      if (!tokensRaw) throw new Error('Missing Wix tokens');
      const tokens = JSON.parse(tokensRaw);
      const wixClient = createClient({ modules: { categories: blogCategoriesModule }, auth: OAuthStrategy({ clientId: '75d88e36-1c76-4009-b769-15f4654556df' }) });
      wixClient.auth.setTokens(tokens);
      const result = await wixClient.categories.queryCategories().find();
      const cats = (result.items || []).map((c: any) => ({ id: c.id, name: c.name || '', description: c.description || '' }));
      setCategories({ categories: cats });
    } catch (error: any) {
      console.error('Failed to load categories:', error);
      alert(`Could not load categories: ${error?.message || 'Unknown error'}`);
    }
  };

  const loadTags = async () => {
    try {
      const tokensRaw = sessionStorage.getItem('wix_tokens');
      if (!tokensRaw) throw new Error('Missing Wix tokens');
      const tokens = JSON.parse(tokensRaw);
      const wixClient = createClient({ modules: { tags: blogTagsModule }, auth: OAuthStrategy({ clientId: '75d88e36-1c76-4009-b769-15f4654556df' }) });
      wixClient.auth.setTokens(tokens);
      const result = await wixClient.tags.queryTags().find();
      const t = (result.items || []).map((it: any) => ({ id: it.id, label: it.label || '' }));
      setTags({ tags: t });
    } catch (error: any) {
      console.error('Failed to load tags:', error);
      alert(`Could not load tags: ${error?.message || 'Unknown error'}`);
    }
  };

  const publishToWix = async () => {
    if (!blogTitle.trim() || !blogContent.trim()) {
      alert('Please enter both title and content');
      return;
    }

    setPublishing(true);
    try {
      // Use test-real endpoint to publish using the client-side access token
      const tokensRaw = sessionStorage.getItem('wix_tokens');
      if (!tokensRaw) throw new Error('Missing Wix tokens. Please reconnect.');
      const tokens = JSON.parse(tokensRaw);
      // For member-level authentication, we don't need to extract member_id
      // The Wix Blog API will automatically use the member ID from the authenticated member token
      const memberIdFromToken = undefined; // Let the API use the authenticated member's ID

      const response = await apiClient.post('/api/wix/test/publish/real', {
        title: blogTitle,
        content: blogContent,
        cover_image_url: coverImageUrl || undefined,
        category_ids: selectedCategory ? [selectedCategory] : undefined,
        tag_ids: selectedTags.length > 0 ? selectedTags : undefined,
        publish: true,
        access_token: tokens?.accessToken?.value || tokens?.access_token,
        member_id: memberIdFromToken
      });

      if (response.data.success) {
        alert(`Blog post published successfully! Post ID: ${response.data.post_id}`);
      } else {
        alert(`Failed to publish: ${response.data.error || response.data.message}`);
      }
    } catch (error: any) {
      console.error('Failed to publish to Wix:', error);
      alert(`Failed to publish: ${error.response?.data?.detail || error.message}`);
    } finally {
      setPublishing(false);
    }
  };

  const disconnectWix = async () => {
    setLoading(true);
    try {
      await apiClient.post('/api/wix/disconnect');
      setConnectionStatus({
        connected: false,
        has_permissions: false,
        error: 'Disconnected'
      });
      setCategories(null);
      setTags(null);
    } catch (error) {
      console.error('Failed to disconnect:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Wix Integration Test Page
      </Typography>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        This page allows you to test the Wix integration functionality. Connect your Wix account 
        and publish blog posts directly from ALwrity to your Wix website.
      </Typography>

      {/* Connection Status Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Wix Connection Status
          </Typography>
          
          {loading ? (
            <Box display="flex" alignItems="center" gap={2}>
              <CircularProgress size={20} />
              <Typography>Checking connection status...</Typography>
            </Box>
          ) : connectionStatus ? (
            <Box>
              {connectionStatus.connected ? (
                <Alert severity="success" sx={{ mb: 2 }}>
                  ✅ Connected to Wix
                  {connectionStatus.has_permissions && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Permissions: Blog creation and publishing enabled
                    </Typography>
                  )}
                </Alert>
              ) : (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  ⚠️ Not connected to Wix
                  {connectionStatus.error && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      {connectionStatus.error}
                    </Typography>
                  )}
                </Alert>
              )}
              
              <Box display="flex" gap={2} flexWrap="wrap">
                {!connectionStatus.connected ? (
                  <Button
                    variant="contained"
                    onClick={getAuthorizationUrl}
                    disabled={loading}
                  >
                    Connect to Wix
                  </Button>
                ) : (
                  <>
                    <Button
                      variant="outlined"
                      onClick={checkConnectionStatus}
                      disabled={loading}
                    >
                      Refresh Status
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={loadCategories}
                      disabled={loading}
                    >
                      Load Categories
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={loadTags}
                      disabled={loading}
                    >
                      Load Tags
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      onClick={disconnectWix}
                      disabled={loading}
                    >
                      Disconnect
                    </Button>
                  </>
                )}
              </Box>
            </Box>
          ) : null}
        </CardContent>
      </Card>

      {/* Blog Post Form */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Publish Blog Post to Wix
          </Typography>
          
          <Box display="flex" flexDirection="column" gap={2}>
            <TextField
              label="Blog Title"
              value={blogTitle}
              onChange={(e) => setBlogTitle(e.target.value)}
              fullWidth
              variant="outlined"
            />
            
            <TextField
              label="Blog Content (Markdown)"
              value={blogContent}
              onChange={(e) => setBlogContent(e.target.value)}
              fullWidth
              multiline
              rows={10}
              variant="outlined"
            />
            
            <TextField
              label="Cover Image URL (Optional)"
              value={coverImageUrl}
              onChange={(e) => setCoverImageUrl(e.target.value)}
              fullWidth
              variant="outlined"
              placeholder="https://example.com/image.jpg"
            />
            
            {categories && (
              <FormControl fullWidth>
                <InputLabel>Category (Optional)</InputLabel>
                <Select
                  value={selectedCategory ?? ''}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  label="Category (Optional)"
                >
                  <MenuItem key="none" value="">
                    None
                  </MenuItem>
                  {categories.categories.map((category, idx) => (
                    <MenuItem key={category.id || `${category.name}-${idx}`} value={category.id}>
                      {category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
            
            {tags && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Tags (Optional)
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {tags.tags.map((tag) => (
                    <Chip
                      key={tag.id}
                      label={tag.label}
                      onClick={() => {
                        if (selectedTags.includes(tag.id)) {
                          setSelectedTags(selectedTags.filter(id => id !== tag.id));
                        } else {
                          setSelectedTags([...selectedTags, tag.id]);
                        }
                      }}
                      color={selectedTags.includes(tag.id) ? 'primary' : 'default'}
                      variant={selectedTags.includes(tag.id) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
              </Box>
            )}
            
            <Divider />
            
            <Button
              variant="contained"
              size="large"
              onClick={publishToWix}
              disabled={publishing || !connectionStatus?.connected}
              sx={{ alignSelf: 'flex-start' }}
            >
              {publishing ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Publishing to Wix...
                </>
              ) : (
                'Publish to Wix'
              )}
            </Button>
            
            {!connectionStatus?.connected && (
              <Alert severity="info">
                Please connect your Wix account first to publish blog posts.
              </Alert>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            How to Use
          </Typography>
          <Typography variant="body2" component="div">
            <ol>
              <li>
                <strong>Connect to Wix:</strong> Click "Connect to Wix" to authorize ALwrity to access your Wix account.
                This will open a new window where you can log in to Wix and grant permissions.
              </li>
              <li>
                <strong>Check Status:</strong> Once connected, you'll see a green success message indicating 
                your Wix account is connected and has the necessary permissions.
              </li>
              <li>
                <strong>Load Categories & Tags:</strong> Click "Load Categories" and "Load Tags" to see 
                available options from your Wix blog.
              </li>
              <li>
                <strong>Create Content:</strong> Enter a title and content for your blog post. 
                You can use Markdown formatting.
              </li>
              <li>
                <strong>Publish:</strong> Click "Publish to Wix" to create and publish the blog post 
                directly to your Wix website.
              </li>
            </ol>
          </Typography>
          
          <Typography variant="body2" sx={{ mt: 2 }}>
            <strong>Note:</strong> This is a test page for development purposes. In the main ALwrity application, 
            this functionality will be integrated into the blog writing workflow.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default WixTestPage;
