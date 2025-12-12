/**
 * Lazy-loaded Wix SDK wrapper
 * 
 * Wix SDK is only used in a few pages (WixTestPage, WixCallbackPage).
 * This wrapper lazy-loads it only when needed.
 */

export const lazyWixSDK = () => import('@wix/sdk');
export const lazyWixBlog = () => import('@wix/blog');

