import React, { useEffect } from 'react';

interface CitationHoverHandlerProps {
  researchSources: any[];
}

// Extend Element interface for our custom property
interface ExtendedElement extends Element {
  _liwTip?: HTMLDivElement | null;
}

const CitationHoverHandler: React.FC<CitationHoverHandlerProps> = ({ researchSources }) => {
  useEffect(() => {
    if (!researchSources || researchSources.length === 0) return;

    console.log('🔍 [Citation Hover] useEffect triggered with', researchSources.length, 'sources');

    // Keep track of currently open tooltip
    let currentOpenTooltip: HTMLDivElement | null = null;

    const initCitationHover = () => {
      try {
        console.log('🔍 [Citation Hover] Script starting...');
        console.log('🔍 [Citation Hover] Research sources count:', researchSources.length);
        
        // Test if script is running
        document.body.style.setProperty('--citation-hover-active', 'true');
        console.log('🔍 [Citation Hover] Script is running, CSS variable set');
        
        // Wait for content to be rendered
        const waitForCitations = () => {
          const citations = document.querySelectorAll('.liw-cite');
          console.log('🔍 [Citation Hover] Looking for citations, found:', citations.length);
          
          if (citations.length === 0) {
            // If no citations found, wait a bit and try again
            console.log('🔍 [Citation Hover] No citations found, waiting...');
            setTimeout(waitForCitations, 200);
            return;
          }
          
          console.log('🔍 [Citation Hover] Found', citations.length, 'citation elements');
          citations.forEach((cite, idx) => {
            console.log(`🔍 [Citation Hover] Citation ${idx}: ${cite.outerHTML}`);
            console.log(`🔍 [Citation Hover] Citation classes: ${cite.className}`);
            console.log(`🔍 [Citation Hover] Citation data-source-index: ${cite.getAttribute('data-source-index')}`);
          });
          setupCitationHover();
        };
        
        const setupCitationHover = () => {
          console.log('🔍 [Citation Hover] Initializing hover functionality...');
          const data = researchSources;
          console.log('🔍 [Citation Hover] Research data loaded:', data.length, 'sources');

          const openOverlay = (idx: string, src: any) => {
            console.log('🔍 [Citation Hover] Opening overlay for source', idx, src);
            const existing = document.getElementById('liw-cite-overlay');
            if (existing) existing.remove();

            const overlay = document.createElement('div');
            overlay.id = 'liw-cite-overlay';
            overlay.style.position = 'fixed';
            overlay.style.inset = '0';
            overlay.style.background = 'rgba(0,0,0,0.35)';
            overlay.style.backdropFilter = 'blur(2px)';
            overlay.style.zIndex = '100000';
            overlay.style.display = 'flex';
            overlay.style.alignItems = 'center';
            overlay.style.justifyContent = 'center';

            const modal = document.createElement('div');
            modal.style.width = 'min(720px, 92vw)';
            modal.style.maxHeight = '80vh';
            modal.style.overflow = 'auto';
            modal.style.borderRadius = '14px';
            modal.style.background = 'linear-gradient(180deg, #ffffff, #f8fdff)';
            modal.style.border = '1px solid #cfe9f7';
            modal.style.boxShadow = '0 24px 80px rgba(10,102,194,0.25)';
            modal.style.padding = '18px 20px';
            
            const title = (src.title || 'Untitled').replace(/</g, '&lt;');
            const url = (src.url || '').replace(/</g, '&lt;');
            const sourceType = src.source_type ? String(src.source_type).replace('_', ' ') : '';
            
            modal.innerHTML = 
              '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">' +
                '<div style="font-size:16px;font-weight:800;color:#0a66c2">Source ' + idx + '</div>' +
                '<button id="liw-cite-close" style="border:none;background:#eff6ff;color:#0a66c2;border-radius:8px;padding:8px 12px;cursor:pointer;font-weight:700">✕ Close</button>' +
              '</div>' +
              '<div style="font-size:18px;font-weight:700;color:#1f2937;margin-bottom:8px">' + title + '</div>' +
              '<a href="' + (src.url || '#') + '" target="_blank" style="display:inline-block;color:#0a66c2;text-decoration:none;margin-bottom:12px;font-size:14px;font-weight:600;">View Source →</a>' +
              (src.content ? '<div style="margin-bottom:16px;color:#374151;font-size:14px;line-height:1.6;background:#f9fafb;padding:16px;border-radius:8px;border-left:4px solid #0a66c2;">' + src.content + '</div>' : '') +
              '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px">' +
                (typeof src.relevance_score === 'number' ? '<span style="background:#eef6ff;border:1px solid #d9ecff;border-radius:999px;padding:8px 12px;font-size:13px;color:#055a8c;font-weight:600">Relevance: ' + Math.round(src.relevance_score * 100) + '%</span>' : '') +
                (typeof src.credibility_score === 'number' ? '<span style="background:#eef6ff;border:1px solid #d9ecff;border-radius:999px;padding:8px 12px;font-size:13px;color:#055a8c;font-weight:600">Credibility: ' + Math.round(src.credibility_score * 100) + '%</span>' : '') +
                (typeof src.domain_authority === 'number' ? '<span style="background:#eef6ff;border:1px solid #d9ecff;border-radius:999px;padding:8px 12px;font-size:13px;color:#055a8c;font-weight:600">Authority: ' + Math.round(src.domain_authority * 100) + '%</span>' : '') +
              '</div>' +
              '<div style="display:flex;gap:16px;color:#6b7280;font-size:13px;padding-top:12px;border-top:1px solid #e5e7eb">' +
                (src.source_type ? '<div>Type: <span style="color:#374151;font-weight:600">' + src.source_type.replace('_', ' ') + '</span></div>' : '') +
                (src.publication_date ? '<div>Published: <span style="color:#374151;font-weight:600">' + src.publication_date + '</span></div>' : '') +
              '</div>' +
              (src.raw_result ? '<div style="color:#6b7280;font-size:12px;margin-top:12px;padding:8px;background:#f3f4f6;border-radius:6px;border-top:1px solid #e5e7eb;">Raw Data: ' + JSON.stringify(src.raw_result).substring(0, 150) + (JSON.stringify(src.raw_result).length > 150 ? '...' : '') + '</div>' : '');

            overlay.appendChild(modal);
            document.body.appendChild(overlay);

            const close = () => { 
              try { overlay.remove(); } catch(_){} 
            };
            overlay.addEventListener('click', (e) => { 
              if(e.target === overlay) close(); 
            });
            document.getElementById('liw-cite-close')?.addEventListener('click', close);
            document.addEventListener('keydown', function esc(ev: KeyboardEvent) { 
              if(ev.key === 'Escape') { 
                close(); 
                document.removeEventListener('keydown', esc);
              } 
            });
          };

          // Add event listeners directly to each citation element
          const citations = document.querySelectorAll('.liw-cite');
          
          citations.forEach((cite) => {
            console.log('🔍 [Citation Hover] Adding event listeners to citation:', cite.outerHTML);
            
            cite.addEventListener('mouseenter', () => {
              console.log('🔍 [Citation Hover] Mouse enter on citation:', cite.outerHTML);
              
              // Close any existing tooltip first
              if (currentOpenTooltip) {
                try { currentOpenTooltip.remove(); } catch(_) {}
                currentOpenTooltip = null;
              }
              
              const idx = cite.getAttribute('data-source-index');
              console.log('🔍 [Citation Hover] Citation index:', idx);
              
              if (!idx) return;
              const i = parseInt(idx, 10) - 1;
              const src = data[i];
              if (!src) {
                console.log('🔍 [Citation Hover] No source found for index:', idx);
                return;
              }

              console.log('🔍 [Citation Hover] Creating tooltip for source:', src);

              let tip = document.createElement('div');
              tip.className = 'liw-cite-tip';
              tip.style.position = 'fixed';
              tip.style.zIndex = '99999';
              tip.style.maxWidth = '420px';
              tip.style.background = 'linear-gradient(180deg, #ffffff, #f8fdff)';
              tip.style.border = '1px solid #cfe9f7';
              tip.style.borderRadius = '10px';
              tip.style.boxShadow = '0 12px 40px rgba(10,102,194,0.18)';
              tip.style.padding = '12px 14px';
              tip.style.fontSize = '12px';
              tip.style.color = '#1f2937';
              tip.style.backdropFilter = 'blur(5px)';
              
              const title = (src.title || 'Untitled').replace(/</g, '&lt;');
              const url = (src.url || '').replace(/</g, '&lt;');
              const sourceType = src.source_type ? String(src.source_type).replace('_', ' ') : '';
              
              tip.innerHTML = 
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">' +
                  '<div style="font-weight:700;color:#0a66c2">Source ' + idx + '</div>' +
                  '<button class="liw-pin" title="Pin" style="border:none;background:#eef6ff;border-radius:8px;padding:4px 8px;cursor:pointer;color:#0a66c2;font-weight:800">📌</button>' +
                '</div>' +
                '<div style="font-weight:600;margin-bottom:6px;color:#1f2937">' + title + '</div>' +
                '<a href="' + (src.url || '#') + '" target="_blank" style="color:#0a66c2;text-decoration:none;margin-bottom:8px;display:block;font-weight:600;">View Source →</a>' +
                (src.content ? '<div style="margin-bottom:8px;color:#374151;font-size:11px;line-height:1.4;background:#f9fafb;padding:8px;border-radius:6px;border-left:3px solid #0a66c2;">' + src.content + '</div>' : '') +
                '<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px">' +
                  (typeof src.relevance_score === 'number' ? '<span style="background:#eef6ff;border:1px solid #d9ecff;border-radius:999px;padding:4px 8px;font-size:11px;color:#055a8c;font-weight:600">Relevance: ' + Math.round(src.relevance_score * 100) + '%</span>' : '') +
                  (typeof src.credibility_score === 'number' ? '<span style="background:#eef6ff;border:1px solid #d9ecff;border-radius:999px;padding:4px 8px;font-size:11px;color:#055a8c;font-weight:600">Credibility: ' + Math.round(src.credibility_score * 100) + '%</span>' : '') +
                  (typeof src.domain_authority === 'number' ? '<span style="background:#eef6ff;border:1px solid #d9ecff;border-radius:999px;padding:4px 8px;font-size:11px;color:#055a8c;font-weight:600">Authority: ' + Math.round(src.domain_authority * 100) + '%</span>' : '') +
                '</div>' +
                (src.source_type ? '<div style="color:#6b7280;font-size:11px;margin-bottom:4px">Type: <span style="color:#374151;font-weight:600">' + src.source_type.replace('_', ' ') + '</span></div>' : '') +
                (src.publication_date ? '<div style="color:#6b7280;font-size:11px">Published: <span style="color:#374151;font-weight:600">' + src.publication_date + '</span></div>' : '') +
                (src.raw_result ? '<div style="color:#6b7280;font-size:11px;margin-top:4px;padding:4px;background:#f3f4f6;border-radius:4px;">Raw Data: ' + JSON.stringify(src.raw_result).substring(0, 100) + (JSON.stringify(src.raw_result).length > 100 ? '...' : '') + '</div>' : '');
                
              document.body.appendChild(tip);
              const rect = cite.getBoundingClientRect();
              tip.style.left = Math.min(rect.left, window.innerWidth - 460) + 'px';
              tip.style.top = (rect.bottom + 8) + 'px';

              tip.querySelector('.liw-pin')?.addEventListener('click', (ev) => {
                ev.stopPropagation();
                openOverlay(idx, src);
                try { tip.remove(); } catch(_) { 
                  // Remove the custom property reference
                  const extendedTip = tip as any;
                  extendedTip._liwTip = undefined;
                }
                currentOpenTooltip = null;
              });

              (cite as ExtendedElement)._liwTip = tip;
              currentOpenTooltip = tip;
              console.log('🔍 [Citation Hover] Tooltip created and positioned');
            });

            cite.addEventListener('mouseleave', () => {
              console.log('🔍 [Citation Hover] Mouse leave on citation:', cite.outerHTML);
              const extendedCite = cite as ExtendedElement;
              if (extendedCite._liwTip) { 
                try { extendedCite._liwTip.remove(); } catch(_) {} 
                extendedCite._liwTip = null; 
                currentOpenTooltip = null;
              }
            });
          });
          
          console.log('✅ [Citation Hover] Hover functionality initialized for', citations.length, 'citations');
        };
        
        // Start waiting for citations with a longer delay to ensure content is rendered
        setTimeout(waitForCitations, 500);
        
      } catch(e: any) { 
        console.warn('liw cite tooltip init failed', e); 
        console.error('Error details:', e);
        // Show error in UI
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'position:fixed;top:10px;right:10px;background:#ffebee;border:1px solid #f44336;border-radius:4px;padding:10px;z-index:100000;color:#c62828;';
        errorDiv.innerHTML = 'Citation hover failed: ' + e.message;
        document.body.appendChild(errorDiv);
        setTimeout(() => errorDiv.remove(), 5000);
      }
    };

    // Initialize citation hover after a short delay to ensure content is rendered
    const timer = setTimeout(initCitationHover, 100);
    
    // Cleanup function
    return () => {
      clearTimeout(timer);
      // Remove any existing tooltips
      const tooltips = document.querySelectorAll('.liw-cite-tip');
      tooltips.forEach(tip => tip.remove());
      // Remove overlay if exists
      const overlay = document.getElementById('liw-cite-overlay');
      if (overlay) overlay.remove();
      // Reset current tooltip reference
      currentOpenTooltip = null;
    };
  }, [researchSources]); // Dependency on researchSources

  // This component doesn't render anything visible
  return null;
};

export default CitationHoverHandler;
