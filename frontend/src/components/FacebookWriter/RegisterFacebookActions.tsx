import React from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { facebookWriterApi, PostGenerateRequest } from '../../services/facebookWriterApi';

const useCopilotActionTyped = useCopilotAction as any;

// Persist minimal user preferences for better defaults across sessions
const PREFS_KEY = 'fbwriter:preferences';
function readPrefs(): Record<string, any> { try { return JSON.parse(localStorage.getItem(PREFS_KEY) || '{}') || {}; } catch { return {}; } }
function writePrefs(p: Record<string, any>) { try { localStorage.setItem(PREFS_KEY, JSON.stringify(p)); } catch {} }

// Allow assistant to log messages into history (handled in FacebookWriter via event)
function logAssistant(content: string) {
  try { window.dispatchEvent(new CustomEvent('fbwriter:assistantMessage', { detail: { content } })); } catch {}
}

const VALID_GOALS = [
  'Promote a product/service',
  'Share valuable content',
  'Increase engagement',
  'Build brand awareness',
  'Drive website traffic',
  'Generate leads',
  'Announce news/updates',
  'Custom'
];

const VALID_TONES = [
  'Informative',
  'Humorous',
  'Inspirational',
  'Upbeat',
  'Casual',
  'Professional',
  'Conversational',
  'Custom'
];

function normalizeEnum(input: string | undefined | null): string {
  return (input || '').trim().toLowerCase();
}

function mapGoal(goal: string | undefined): string {
  const g = normalizeEnum(goal);
  if (!g) return 'Build brand awareness';
  const exact = VALID_GOALS.find(v => v.toLowerCase() === g);
  if (exact) return exact;
  if (g.includes('announce')) return 'Announce news/updates';
  if (g.includes('awareness') || g.includes('brand')) return 'Build brand awareness';
  if (g.includes('engagement') || g.includes('engage')) return 'Increase engagement';
  if (g.includes('traffic')) return 'Drive website traffic';
  if (g.includes('lead')) return 'Generate leads';
  if (g.includes('share') || g.includes('content')) return 'Share valuable content';
  if (g.includes('promote') || g.includes('product') || g.includes('service')) return 'Promote a product/service';
  return 'Build brand awareness';
}

function mapTone(tone: string | undefined): string {
  const t = normalizeEnum(tone);
  if (!t) return 'Professional';
  const exact = VALID_TONES.find(v => v.toLowerCase() === t);
  if (exact) return exact;
  if (t.includes('friendly') || t.includes('casual')) return 'Casual';
  if (t.includes('professional') || t.includes('pro')) return 'Professional';
  if (t.includes('exciting') || t.includes('energetic') || t.includes('upbeat')) return 'Upbeat';
  if (t.includes('inspir')) return 'Inspirational';
  if (t.includes('humor') || t.includes('funny')) return 'Humorous';
  if (t.includes('convers')) return 'Conversational';
  if (t.includes('info')) return 'Informative';
  return 'Professional';
}

const PostHITL: React.FC<{ args: any; respond: (data: any) => void }> = ({ args, respond }) => {
  const prefs = React.useMemo(() => readPrefs(), []);
  const [form, setForm] = React.useState<PostGenerateRequest>({
    business_type: args?.business_type || prefs.business_type || 'SaaS',
    target_audience: args?.target_audience || prefs.target_audience || 'Marketing managers at SMEs',
    post_goal: args?.post_goal || prefs.post_goal || 'Build brand awareness',
    post_tone: args?.post_tone || prefs.post_tone || 'Professional',
    include: args?.include || prefs.include || '',
    avoid: args?.avoid || prefs.avoid || '',
    media_type: args?.media_type || 'None',
    advanced_options: { use_hook: true, use_story: true, use_cta: true, use_question: true, use_emoji: true, use_hashtags: true }
  });
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const run = async () => {
    try {
      setLoading(true);
      setError(null);
      const payload: PostGenerateRequest = {
        ...form,
        post_goal: mapGoal(form.post_goal),
        post_tone: mapTone(form.post_tone),
        media_type: 'None'
      };
      // Save user preference snapshot
      writePrefs({
        business_type: payload.business_type,
        target_audience: payload.target_audience,
        post_goal: payload.post_goal,
        post_tone: payload.post_tone,
        include: payload.include,
        avoid: payload.avoid
      });
      const res = await facebookWriterApi.postGenerate(payload);
      const content = res?.content || res?.data?.content;
      if (content) {
        window.dispatchEvent(new CustomEvent('fbwriter:updateDraft', { detail: content }));
        logAssistant(content);
        respond({ success: true, content });
      } else {
        respond({ success: true, message: 'Post generated.' });
      }
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || 'Failed to generate post';
      const tip = `Tip: goals must be one of ${VALID_GOALS.join(', ')}; tones must be one of ${VALID_TONES.join(', ')}.`;
      setError(`${msg}`);
      respond({ success: false, message: `${msg}` });
      console.error('[FB Writer] post.generate error', e);
    } finally {
      setLoading(false);
    }
  };

  const set = (k: keyof PostGenerateRequest, v: any) => setForm(prev => ({ ...prev, [k]: v }));

  return (
    <div style={{ padding: 12 }}>
      <div style={{ fontWeight: 600, marginBottom: 8 }}>Generate Facebook Post</div>
      <div style={{ display: 'grid', gap: 8 }}>
        <input placeholder={`Business type`} value={form.business_type} onChange={e => set('business_type', e.target.value)} />
        <input placeholder={`Target audience`} value={form.target_audience} onChange={e => set('target_audience', e.target.value)} />
        <input placeholder={`Goal (e.g., ${VALID_GOALS[3]})`} value={form.post_goal} onChange={e => set('post_goal', e.target.value)} />
        <input placeholder={`Tone (e.g., ${VALID_TONES[5]})`} value={form.post_tone} onChange={e => set('post_tone', e.target.value)} />
        <input placeholder="Include" value={form.include || ''} onChange={e => set('include', e.target.value)} />
        <input placeholder="Avoid" value={form.avoid || ''} onChange={e => set('avoid', e.target.value)} />
      </div>
      <button onClick={run} disabled={loading} style={{ marginTop: 8 }}>{loading ? 'Generating…' : 'Generate'}</button>
      {error && <div style={{ marginTop: 8, color: '#c33', fontSize: 12 }}>{error}</div>}
    </div>
  );
};

const HashtagsHITL: React.FC<{ args: any; respond: (data: any) => void }> = ({ args, respond }) => {
  const [topic, setTopic] = React.useState<string>(args?.content_topic || 'product launch');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const run = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await facebookWriterApi.hashtagsGenerate({ content_topic: topic });
      console.log('Hashtag generation response:', res);
      
      const hashtags = res?.hashtags || res?.data?.hashtags;
      if (Array.isArray(hashtags) && hashtags.length) {
        const line = hashtags.join(' ');
        window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: `\n\n${line}` }));
        logAssistant(line);
        respond({ success: true, hashtags });
      } else {
        console.log('No hashtags found in response:', res);
        respond({ success: true, message: 'Hashtags generated.' });
      }
    } catch (e: any) {
      console.error('[FB Writer] hashtags.generate error:', e);
      const msg = e?.response?.data?.detail || e?.message || 'Failed to generate hashtags';
      setError(`${msg}`);
      respond({ success: false, message: `${msg}` });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div style={{ padding: 12 }}>
      <div style={{ fontWeight: 600, marginBottom: 8 }}>Generate Hashtags</div>
      <input placeholder="Topic" value={topic} onChange={e => setTopic(e.target.value)} />
      <button onClick={run} disabled={loading} style={{ marginLeft: 8 }}>{loading ? 'Generating…' : 'Generate'}</button>
      {error && <div style={{ marginTop: 8, color: '#c33', fontSize: 12 }}>{error}</div>}
    </div>
  );
};

const RegisterFacebookActions: React.FC = () => {
  useCopilotActionTyped({
    name: 'generateFacebookEvent',
    description: 'Generate a Facebook Event title and description',
    parameters: [
      { name: 'event_name', type: 'string', required: false },
      { name: 'event_type', type: 'string', required: false },
      { name: 'event_format', type: 'string', required: false },
      { name: 'business_type', type: 'string', required: false },
      { name: 'target_audience', type: 'string', required: false }
    ],
    renderAndWaitForResponse: ({ args, respond }: any) => {
      const TYPES = ['Workshop','Webinar','Conference','Networking event','Product launch','Sale/Promotion','Community event','Educational event','Custom'];
      const FORMATS = ['In-person','Virtual','Hybrid'];
      const mapType = (t?: string) => {
        const s = (t || '').trim().toLowerCase();
        const exact = TYPES.find(v => v.toLowerCase() === s);
        if (exact) return exact;
        if (s.includes('web')) return 'Webinar';
        if (s.includes('work')) return 'Workshop';
        if (s.includes('network')) return 'Networking event';
        if (s.includes('launch')) return 'Product launch';
        if (s.includes('sale') || s.includes('promo')) return 'Sale/Promotion';
        if (s.includes('communi')) return 'Community event';
        if (s.includes('educat')) return 'Educational event';
        if (s.includes('conf')) return 'Conference';
        return 'Webinar';
      };
      const mapFormat = (f?: string) => {
        const s = (f || '').trim().toLowerCase();
        const exact = FORMATS.find(v => v.toLowerCase() === s);
        if (exact) return exact;
        if (s.includes('in') || s.includes('person')) return 'In-person';
        if (s.includes('hybr')) return 'Hybrid';
        return 'Virtual';
      };
      const EventHITL: React.FC = () => {
        const [form, setForm] = React.useState({
          event_name: args?.event_name || 'Monthly Growth Webinar',
          event_type: mapType(args?.event_type) || 'Webinar',
          event_format: mapFormat(args?.event_format) || 'Virtual',
          business_type: args?.business_type || 'SaaS',
          target_audience: args?.target_audience || 'Marketing managers at SMEs',
          event_date: args?.event_date || '',
          event_time: args?.event_time || '',
          location: args?.location || '',
          duration: args?.duration || '60 minutes',
          key_benefits: args?.key_benefits || '',
          speakers: args?.speakers || '',
          agenda: args?.agenda || '',
          ticket_info: args?.ticket_info || '',
          special_offers: args?.special_offers || '',
          include: args?.include || '',
          avoid: args?.avoid || ''
        });
        const [loading, setLoading] = React.useState(false);
        const [error, setError] = React.useState<string | null>(null);
        const run = async () => {
          try {
            setLoading(true);
            setError(null);
            const payload = { ...form, event_type: mapType(form.event_type), event_format: mapFormat(form.event_format) } as any;
            const res = await facebookWriterApi.eventGenerate(payload);
            const title = res?.event_title || res?.data?.event_title;
            const desc = res?.event_description || res?.data?.event_description;
            let out = '';
            if (title) out += `\n\n${title}`;
            if (desc) out += `\n\n${desc}`;
            if (out) {
              window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: out }));
              respond({ success: true, content: out });
            } else {
              respond({ success: true, message: 'Event generated.' });
            }
          } catch (e: any) {
            const msg = e?.response?.data?.detail || e?.message || 'Failed to generate event';
            setError(`${msg}`);
            respond({ success: false, message: `${msg}` });
          } finally {
            setLoading(false);
          }
        };
        const set = (k: string, v: any) => setForm((p: any) => ({ ...p, [k]: v }));
        return (
          <div style={{ padding: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 8 }}>Generate Event</div>
            <div style={{ display: 'grid', gap: 8 }}>
              <input placeholder="Event name" value={form.event_name} onChange={e => set('event_name', e.target.value)} />
              <input placeholder="Event type (e.g., Webinar)" value={form.event_type} onChange={e => set('event_type', e.target.value)} />
              <input placeholder="Format (In-person/Virtual/Hybrid)" value={form.event_format} onChange={e => set('event_format', e.target.value)} />
              <input placeholder="Business type" value={form.business_type} onChange={e => set('business_type', e.target.value)} />
              <input placeholder="Target audience" value={form.target_audience} onChange={e => set('target_audience', e.target.value)} />
              <input placeholder="Date (YYYY-MM-DD)" value={form.event_date} onChange={e => set('event_date', e.target.value)} />
              <input placeholder="Time" value={form.event_time} onChange={e => set('event_time', e.target.value)} />
              <input placeholder="Location" value={form.location} onChange={e => set('location', e.target.value)} />
              <input placeholder="Duration" value={form.duration} onChange={e => set('duration', e.target.value)} />
              <input placeholder="Key benefits" value={form.key_benefits} onChange={e => set('key_benefits', e.target.value)} />
              <input placeholder="Speakers" value={form.speakers} onChange={e => set('speakers', e.target.value)} />
              <input placeholder="Agenda" value={form.agenda} onChange={e => set('agenda', e.target.value)} />
              <input placeholder="Ticket info" value={form.ticket_info} onChange={e => set('ticket_info', e.target.value)} />
              <input placeholder="Special offers" value={form.special_offers} onChange={e => set('special_offers', e.target.value)} />
              <input placeholder="Include" value={form.include} onChange={e => set('include', e.target.value)} />
              <input placeholder="Avoid" value={form.avoid} onChange={e => set('avoid', e.target.value)} />
            </div>
            <button onClick={run} disabled={loading} style={{ marginTop: 8 }}>{loading ? 'Generating…' : 'Generate'}</button>
            {error && <div style={{ marginTop: 8, color: '#c33', fontSize: 12 }}>{error}</div>}
          </div>
        );
      };
      return <EventHITL />;
    },
    handler: async (args: any) => {
      const TYPES = ['Workshop','Webinar','Conference','Networking event','Product launch','Sale/Promotion','Community event','Educational event','Custom'];
      const FORMATS = ['In-person','Virtual','Hybrid'];
      const map = (arr: string[], v: string | undefined, def: string) => {
        const s = (v || '').trim().toLowerCase();
        const exact = arr.find(x => x.toLowerCase() === s);
        return exact || def;
      };
      const res = await facebookWriterApi.eventGenerate({
        event_name: args?.event_name || 'Monthly Growth Webinar',
        event_type: map(TYPES, args?.event_type, 'Webinar'),
        event_format: map(FORMATS, args?.event_format, 'Virtual'),
        business_type: args?.business_type || 'SaaS',
        target_audience: args?.target_audience || 'Marketing managers at SMEs',
        event_date: args?.event_date,
        event_time: args?.event_time,
        location: args?.location,
        duration: args?.duration,
        key_benefits: args?.key_benefits,
        speakers: args?.speakers,
        agenda: args?.agenda,
        ticket_info: args?.ticket_info,
        special_offers: args?.special_offers,
        include: args?.include,
        avoid: args?.avoid
      });
      const title = res?.event_title || res?.data?.event_title;
      const desc = res?.event_description || res?.data?.event_description;
      let out = '';
      if (title) out += `\n\n${title}`;
      if (desc) out += `\n\n${desc}`;
      if (out) {
        window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: out }));
        return { success: true, content: out };
      }
      return { success: true, message: 'Event generated.' };
    }
  });
  useCopilotActionTyped({
    name: 'generateFacebookCarousel',
    description: 'Generate a Facebook Carousel with slides and a main caption',
    parameters: [
      { name: 'business_type', type: 'string', required: false },
      { name: 'target_audience', type: 'string', required: false },
      { name: 'carousel_type', type: 'string', required: false },
      { name: 'topic', type: 'string', required: false }
    ],
    renderAndWaitForResponse: ({ args, respond }: any) => {
      const VALID_TYPES = ['Product showcase','Step-by-step guide','Before/After','Customer testimonials','Features & Benefits','Portfolio showcase','Educational content','Custom'];
      const mapType = (t?: string) => {
        const s = (t || '').trim().toLowerCase();
        const exact = VALID_TYPES.find(v => v.toLowerCase() === s);
        if (exact) return exact;
        if (s.includes('step')) return 'Step-by-step guide';
        if (s.includes('before') || s.includes('after')) return 'Before/After';
        if (s.includes('testi')) return 'Customer testimonials';
        if (s.includes('feature') || s.includes('benefit')) return 'Features & Benefits';
        if (s.includes('portfolio')) return 'Portfolio showcase';
        if (s.includes('educat')) return 'Educational content';
        return 'Product showcase';
      };
      const CarouselHITL: React.FC = () => {
        const prefs = React.useMemo(() => readPrefs(), []);
        const [form, setForm] = React.useState({
          business_type: args?.business_type || prefs.business_type || 'SaaS',
          target_audience: args?.target_audience || prefs.target_audience || 'Marketing managers at SMEs',
          carousel_type: args?.carousel_type || 'Product showcase',
          topic: args?.topic || 'Feature breakdown',
          num_slides: 5,
          include_cta: true,
          cta_text: '',
          brand_colors: '',
          include: '',
          avoid: ''
        });
        const [loading, setLoading] = React.useState(false);
        const [error, setError] = React.useState<string | null>(null);
        const run = async () => {
          try {
            setLoading(true);
            setError(null);
            const payload = { ...form, carousel_type: mapType(form.carousel_type) } as any;
            const res = await facebookWriterApi.carouselGenerate(payload);
            const main = res?.main_caption || res?.data?.main_caption;
            const slides = res?.slides || res?.data?.slides;
            let out = '';
            if (main) out += `\n\n${main}`;
            if (Array.isArray(slides)) {
              out += '\n\nCarousel Slides:';
              slides.forEach((s: any, i: number) => {
                out += `\n${i + 1}. ${s.title}: ${s.content}`;
              });
            }
            if (out) {
              window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: out }));
              logAssistant(out);
              respond({ success: true, content: out });
            } else {
              respond({ success: true, message: 'Carousel generated.' });
            }
          } catch (e: any) {
            const msg = e?.response?.data?.detail || e?.message || 'Failed to generate carousel';
            setError(`${msg}`);
            respond({ success: false, message: `${msg}` });
          } finally {
            setLoading(false);
          }
        };
        const set = (k: string, v: any) => setForm((p: any) => ({ ...p, [k]: v }));
        return (
          <div style={{ padding: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 8 }}>Generate Carousel</div>
            <div style={{ display: 'grid', gap: 8 }}>
              <input placeholder="Business type" value={form.business_type} onChange={e => set('business_type', e.target.value)} />
              <input placeholder="Target audience" value={form.target_audience} onChange={e => set('target_audience', e.target.value)} />
              <input placeholder="Carousel type (e.g., Product showcase)" value={form.carousel_type} onChange={e => set('carousel_type', e.target.value)} />
              <input placeholder="Topic" value={form.topic} onChange={e => set('topic', e.target.value)} />
              <input placeholder="Number of slides (3-10)" value={form.num_slides} onChange={e => set('num_slides', Number(e.target.value) || 5)} />
              <label><input type="checkbox" checked={!!form.include_cta} onChange={e => set('include_cta', e.target.checked)} /> Include CTA</label>
              <input placeholder="CTA text" value={form.cta_text} onChange={e => set('cta_text', e.target.value)} />
              <input placeholder="Brand colors" value={form.brand_colors} onChange={e => set('brand_colors', e.target.value)} />
              <input placeholder="Include" value={form.include} onChange={e => set('include', e.target.value)} />
              <input placeholder="Avoid" value={form.avoid} onChange={e => set('avoid', e.target.value)} />
            </div>
            <button onClick={run} disabled={loading} style={{ marginTop: 8 }}>{loading ? 'Generating…' : 'Generate'}</button>
            {error && <div style={{ marginTop: 8, color: '#c33', fontSize: 12 }}>{error}</div>}
          </div>
        );
      };
      return <CarouselHITL />;
    },
    handler: async (args: any) => {
      const VALID_TYPES = ['Product showcase','Step-by-step guide','Before/After','Customer testimonials','Features & Benefits','Portfolio showcase','Educational content','Custom'];
      const mapType = (t?: string) => {
        const s = (t || '').trim().toLowerCase();
        const exact = VALID_TYPES.find(v => v.toLowerCase() === s);
        return exact || 'Product showcase';
      };
      // If we only want images: gate by provider availability
      try {
        const health = await facebookWriterApi.health();
        const available = !!health?.image_providers?.available;
        if (!available) {
          const msg = 'Image generation not configured. Please set GEMINI_API_KEY (or Nano Banana) in backend/.env and restart.';
          window.dispatchEvent(new CustomEvent('fbwriter:assistantMessage', { detail: { content: msg } }));
          return { success: false, message: msg };
        }
      } catch {}

      // Generate carousel images using the new Facebook image generation endpoint
      const carouselImages = [];
      const numSlides = Math.min(10, Math.max(3, Number(args?.num_slides) || 5));
      
      for (let i = 0; i < numSlides; i++) {
        try {
          const slidePrompt = `${args?.topic || 'Feature breakdown'} - Slide ${i + 1} of ${numSlides}, ${mapType(args?.carousel_type)} style`;
          const imgRes = await facebookWriterApi.generateFacebookImageNew({
            prompt: slidePrompt,
            aspect_ratio: '1:1',
            content_context: {
              content_type: 'carousel',
        topic: args?.topic || 'Feature breakdown',
              business_type: args?.business_type || 'general',
              slide_number: i + 1,
              total_slides: numSlides
            }
          });
          
          if (imgRes?.images && imgRes.images.length > 0) {
            carouselImages.push(imgRes.images[0]);
          }
        } catch (err) {
          console.warn(`Failed to generate image for slide ${i + 1}:`, err);
        }
      }
      
      if (carouselImages.length > 0) {
        window.dispatchEvent(new CustomEvent('fbwriter:storyImages', { detail: carouselImages }));
        return { success: true, count: carouselImages.length };
      }
      return { success: false, message: 'No images generated. Check API keys/billing.' };
    }
  });
  useCopilotActionTyped({
    name: 'generateFacebookReel',
    description: 'Generate a Facebook Reel script with scene breakdown and music suggestions',
    parameters: [
      { name: 'business_type', type: 'string', required: false },
      { name: 'target_audience', type: 'string', required: false },
      { name: 'reel_type', type: 'string', required: false },
      { name: 'reel_length', type: 'string', required: false },
      { name: 'reel_style', type: 'string', required: false },
      { name: 'topic', type: 'string', required: false }
    ],
    renderAndWaitForResponse: ({ args, respond }: any) => {
      const VALID_REEL_TYPES = ['Product demonstration','Tutorial/How-to','Entertainment','Educational','Trend-based','Behind the scenes','User-generated content','Custom'];
      const VALID_REEL_LENGTHS = ['15-30 seconds','30-60 seconds','60-90 seconds'];
      const VALID_REEL_STYLES = ['Fast-paced','Relaxed','Dramatic','Minimalist','Vibrant','Custom'];
      const mapReelType = (t?: string) => {
        const s = (t || '').trim().toLowerCase();
        const exact = VALID_REEL_TYPES.find(v => v.toLowerCase() === s);
        if (exact) return exact;
        if (s.includes('product')) return 'Product demonstration';
        if (s.includes('tutorial') || s.includes('how')) return 'Tutorial/How-to';
        if (s.includes('behind')) return 'Behind the scenes';
        if (s.includes('user')) return 'User-generated content';
        if (s.includes('trend')) return 'Trend-based';
        if (s.includes('educat')) return 'Educational';
        if (s.includes('entertain')) return 'Entertainment';
        return 'Product demonstration';
      };
      const mapReelLength = (l?: string) => {
        const s = (l || '').trim().toLowerCase();
        const exact = VALID_REEL_LENGTHS.find(v => v.toLowerCase() === s);
        if (exact) return exact;
        if (s.includes('15')) return '15-30 seconds';
        if (s.includes('60') || s.includes('30-60')) return '30-60 seconds';
        if (s.includes('90') || s.includes('60-90')) return '60-90 seconds';
        return '30-60 seconds';
      };
      const mapReelStyle = (st?: string) => {
        const s = (st || '').trim().toLowerCase();
        const exact = VALID_REEL_STYLES.find(v => v.toLowerCase() === s);
        if (exact) return exact;
        if (s.includes('fast')) return 'Fast-paced';
        if (s.includes('relax')) return 'Relaxed';
        if (s.includes('dram')) return 'Dramatic';
        if (s.includes('mini')) return 'Minimalist';
        if (s.includes('vibr')) return 'Vibrant';
        return 'Fast-paced';
      };
      const ReelHITL: React.FC = () => {
        const prefs = React.useMemo(() => readPrefs(), []);
        const [form, setForm] = React.useState({
          business_type: args?.business_type || prefs.business_type || 'SaaS',
          target_audience: args?.target_audience || prefs.target_audience || 'Marketing managers at SMEs',
          reel_type: args?.reel_type || 'Product demonstration',
          reel_length: args?.reel_length || '30-60 seconds',
          reel_style: args?.reel_style || 'Fast-paced',
          topic: args?.topic || 'Feature walkthrough',
          include: args?.include || '',
          avoid: args?.avoid || '',
          music_preference: args?.music_preference || ''
        });
        const [loading, setLoading] = React.useState(false);
        const [error, setError] = React.useState<string | null>(null);
        const run = async () => {
          try {
            setLoading(true);
            setError(null);
            const payload = {
              ...form,
              reel_type: mapReelType(form.reel_type),
              reel_length: mapReelLength(form.reel_length),
              reel_style: mapReelStyle(form.reel_style)
            } as any;
            const res = await facebookWriterApi.reelGenerate(payload);
            const script = res?.script || res?.data?.script;
            if (script) {
              window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: `\n\n${script}` }));
              logAssistant(script);
              respond({ success: true, content: script });
            } else {
              respond({ success: true, message: 'Reel generated.' });
            }
          } catch (e: any) {
            const msg = e?.response?.data?.detail || e?.message || 'Failed to generate reel. Tip: type should be one of ' + VALID_REEL_TYPES.join(', ') + '; length one of ' + VALID_REEL_LENGTHS.join(', ') + '; style one of ' + VALID_REEL_STYLES.join(', ') + '.';
            setError(`${msg}`);
            respond({ success: false, message: `${msg}` });
          } finally {
            setLoading(false);
          }
        };
        const set = (k: string, v: any) => setForm((p: any) => ({ ...p, [k]: v }));
        return (
          <div style={{ padding: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 8 }}>Generate Reel</div>
            <div style={{ display: 'grid', gap: 8 }}>
              <input placeholder="Business type" value={form.business_type} onChange={e => set('business_type', e.target.value)} />
              <input placeholder="Target audience" value={form.target_audience} onChange={e => set('target_audience', e.target.value)} />
              <input placeholder="Reel type (e.g., Product demonstration)" value={form.reel_type} onChange={e => set('reel_type', e.target.value)} />
              <input placeholder="Length (e.g., 30-60 seconds)" value={form.reel_length} onChange={e => set('reel_length', e.target.value)} />
              <input placeholder="Style (e.g., Fast-paced)" value={form.reel_style} onChange={e => set('reel_style', e.target.value)} />
              <input placeholder="Topic" value={form.topic} onChange={e => set('topic', e.target.value)} />
              <input placeholder="Include" value={form.include} onChange={e => set('include', e.target.value)} />
              <input placeholder="Avoid" value={form.avoid} onChange={e => set('avoid', e.target.value)} />
              <input placeholder="Music preference" value={form.music_preference} onChange={e => set('music_preference', e.target.value)} />
            </div>
            <button onClick={run} disabled={loading} style={{ marginTop: 8 }}>{loading ? 'Generating…' : 'Generate'}</button>
            {error && <div style={{ marginTop: 8, color: '#c33', fontSize: 12 }}>{error}</div>}
          </div>
        );
      };
      return <ReelHITL />;
    },
    handler: async (args: any) => {
      const VALID_REEL_TYPES = ['Product demonstration','Tutorial/How-to','Entertainment','Educational','Trend-based','Behind the scenes','User-generated content','Custom'];
      const VALID_REEL_LENGTHS = ['15-30 seconds','30-60 seconds','60-90 seconds'];
      const VALID_REEL_STYLES = ['Fast-paced','Relaxed','Dramatic','Minimalist','Vibrant','Custom'];
      const map = (arr: string[], s: string | undefined, fallback: string) => {
        const t = (s || '').trim().toLowerCase();
        const exact = arr.find(v => v.toLowerCase() === t);
        return exact || fallback;
      };
      const res = await facebookWriterApi.reelGenerate({
        business_type: args?.business_type,
        target_audience: args?.target_audience,
        reel_type: map(VALID_REEL_TYPES, args?.reel_type, 'Product demonstration'),
        reel_length: map(VALID_REEL_LENGTHS, args?.reel_length, '30-60 seconds'),
        reel_style: map(VALID_REEL_STYLES, args?.reel_style, 'Fast-paced'),
        topic: args?.topic || 'Feature walkthrough',
        include: args?.include,
        avoid: args?.avoid,
        music_preference: args?.music_preference
      });
      const script = res?.script || res?.data?.script;
      if (script) {
        window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: `\n\n${script}` }));
        return { success: true, content: script };
      }
      return { success: true, message: 'Reel generated.' };
    }
  });
  useCopilotActionTyped({
    name: 'generateFacebookPost',
    description: 'Generate a Facebook post using AI',
    parameters: [
      { name: 'business_type', type: 'string', required: false },
      { name: 'target_audience', type: 'string', required: false },
      { name: 'post_goal', type: 'string', required: false },
      { name: 'post_tone', type: 'string', required: false }
    ],
    renderAndWaitForResponse: ({ args, respond }: any) => <PostHITL args={args} respond={respond} />,
    handler: async (args: any) => {
      const payload: PostGenerateRequest = {
        ...(args || {}),
        post_goal: mapGoal(args?.post_goal),
        post_tone: mapTone(args?.post_tone),
        media_type: 'None'
      };
      
      // Trigger progress indicator
      window.dispatchEvent(new CustomEvent('fbwriter:generatingStart'));
      window.dispatchEvent(new CustomEvent('fbwriter:setGenerationType', { detail: 'post' }));
      
      try {
      const res = await facebookWriterApi.postGenerate(payload);
      const content = res?.content || res?.data?.content;
      if (content) {
          // Use the new copyToDraft action to ensure proper UI sync
        window.dispatchEvent(new CustomEvent('fbwriter:updateDraft', { detail: content }));
          window.dispatchEvent(new CustomEvent('fbwriter:generatingEnd'));
          return { 
            success: true, 
            content,
            message: 'Facebook post generated and copied to draft successfully'
          };
        }
        window.dispatchEvent(new CustomEvent('fbwriter:generatingEnd'));
      return { success: true, message: 'Post generated.' };
      } catch (error) {
        window.dispatchEvent(new CustomEvent('fbwriter:generatingEnd'));
        throw error;
      }
    }
  });

  useCopilotActionTyped({
    name: 'generateFacebookHashtags',
    description: 'Generate relevant hashtags for the content',
    parameters: [
      { name: 'content_topic', type: 'string', required: false }
    ],
    renderAndWaitForResponse: ({ args, respond }: any) => <HashtagsHITL args={args} respond={respond} />,
    handler: async (args: any) => {
      // Trigger progress indicator
      window.dispatchEvent(new CustomEvent('fbwriter:generatingStart'));
      window.dispatchEvent(new CustomEvent('fbwriter:setGenerationType', { detail: 'hashtags' }));
      
      try {
      const res = await facebookWriterApi.hashtagsGenerate({ content_topic: args?.content_topic });
      const hashtags = res?.hashtags || res?.data?.hashtags;
      if (Array.isArray(hashtags) && hashtags.length) {
        const line = hashtags.join(' ');
        window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: `\n\n${line}` }));
          window.dispatchEvent(new CustomEvent('fbwriter:generatingEnd'));
        return { success: true, hashtags };
      }
        window.dispatchEvent(new CustomEvent('fbwriter:generatingEnd'));
      return { success: true, message: 'Hashtags generated.' };
      } catch (error) {
        window.dispatchEvent(new CustomEvent('fbwriter:generatingEnd'));
        throw error;
      }
    }
  });

  // New action to copy generated content to draft
  useCopilotActionTyped({
    name: 'copyToDraft',
    description: 'Copy generated Facebook post content to the main draft area',
    parameters: [
      { name: 'content', type: 'string', required: true, description: 'The Facebook post content to copy to draft' },
      { name: 'replace', type: 'boolean', required: false, description: 'Whether to replace existing draft (true) or append (false)' }
    ],
    handler: async (args: any) => {
      try {
        const content = args?.content || '';
        const replace = args?.replace !== false; // Default to replace
        
        if (!content || content.trim().length === 0) {
          return { success: false, error: 'No content provided to copy to draft' };
        }

        // Clean up the content
        const cleanContent = content
          .replace(/^Here's a.*?:\s*/i, '')
          .replace(/^Facebook post[:\s]*/i, '')
          .replace(/```[\s\S]*?```/g, '')
          .trim();

        if (cleanContent.length < 10) {
          return { success: false, error: 'Content too short to be a valid Facebook post' };
        }

        // Dispatch the appropriate event
        if (replace) {
          window.dispatchEvent(new CustomEvent('fbwriter:updateDraft', { detail: cleanContent }));
        } else {
          window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: cleanContent }));
        }

        console.log('📝 Copilot copied content to draft:', cleanContent.substring(0, 100) + '...');
        
        return { 
          success: true, 
          message: `Content ${replace ? 'copied to' : 'appended to'} draft successfully`,
          content: cleanContent,
          action: replace ? 'replaced' : 'appended'
        };
      } catch (error) {
        console.error('Error copying content to draft:', error);
        return { 
          success: false, 
          error: `Failed to copy content to draft: ${error}` 
        };
      }
    }
  });

  // Ad Copy generation (M3)
  const AdCopyHITL: React.FC<{ args: any; respond?: (data: any) => void }> = ({ args, respond }) => {
    const prefs = React.useMemo(() => readPrefs(), []);
    const [form, setForm] = React.useState({
      business_type: args?.business_type || prefs.business_type || 'SaaS',
      product_service: args?.product_service || 'Product X',
      ad_objective: args?.ad_objective || 'Conversions',
      ad_format: args?.ad_format || 'Single image',
      target_audience: args?.target_audience || prefs.target_audience || 'Marketing managers at SMEs',
      targeting_options: {
        age_group: (args?.targeting_options?.age_group) || '18-24',
        gender: args?.targeting_options?.gender || 'All',
        location: args?.targeting_options?.location || 'Global',
        interests: args?.targeting_options?.interests || '',
        behaviors: args?.targeting_options?.behaviors || '',
        lookalike_audience: args?.targeting_options?.lookalike_audience || ''
      },
      unique_selling_proposition: args?.unique_selling_proposition || 'Fast, reliable, loved by users',
      offer_details: args?.offer_details || '',
      budget_range: args?.budget_range || '$50-200/day',
      custom_budget: args?.custom_budget || '',
      campaign_duration: args?.campaign_duration || '2 weeks',
      competitor_analysis: args?.competitor_analysis || '',
      brand_voice: args?.brand_voice || (prefs.post_tone || 'Professional'),
      compliance_requirements: args?.compliance_requirements || ''
    });
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const safeRespond = React.useCallback((data: any) => {
      try {
        if (typeof respond === 'function') respond(data);
        else console.log('[FB Writer][HITL] respond unavailable; payload:', data);
      } catch (e) { console.warn('[FB Writer][HITL] respond error', e); }
    }, [respond]);

    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await facebookWriterApi.adCopyGenerate(form as any);
        const variations = {
          headline_variations: res?.ad_variations?.headline_variations || res?.data?.ad_variations?.headline_variations || [],
          primary_text_variations: res?.ad_variations?.primary_text_variations || res?.data?.ad_variations?.primary_text_variations || [],
          description_variations: res?.ad_variations?.description_variations || res?.data?.ad_variations?.description_variations || [],
          cta_variations: res?.ad_variations?.cta_variations || res?.data?.ad_variations?.cta_variations || []
        };
        window.dispatchEvent(new CustomEvent('fbwriter:adVariations', { detail: variations }));
        const primaryObj = res?.primary_ad_copy || res?.data?.primary_ad_copy;
        const message = primaryObj?.primary_text || primaryObj?.text || res?.content || res?.data?.content || 'Ad copy generated.';
        window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: `\n\n${message}` }));
        logAssistant(message);
        safeRespond({ success: true, content: message });
      } catch (e: any) {
        const msg = e?.response?.data?.detail || e?.message || 'Failed to generate ad copy';
        setError(`${msg}`);
        safeRespond({ success: false, message: `${msg}` });
      } finally {
        setLoading(false);
      }
    };

    const set = (k: string, v: any) => setForm((prev: any) => ({ ...prev, [k]: v }));
    const setNested = (k: keyof typeof form.targeting_options, v: any) => setForm((prev: any) => ({ ...prev, targeting_options: { ...prev.targeting_options, [k]: v } }));

    return (
      <div style={{ padding: 12 }}>
        <div style={{ fontWeight: 600, marginBottom: 8 }}>Generate Ad Copy</div>
        <div style={{ display: 'grid', gap: 8 }}>
          <input placeholder="Business type" value={form.business_type} onChange={e => set('business_type', e.target.value)} />
          <input placeholder="Product/Service" value={form.product_service} onChange={e => set('product_service', e.target.value)} />
          <input placeholder="Ad objective (e.g., Conversions)" value={form.ad_objective} onChange={e => set('ad_objective', e.target.value)} />
          <input placeholder="Ad format (e.g., Single image)" value={form.ad_format} onChange={e => set('ad_format', e.target.value)} />
          <input placeholder="Target audience" value={form.target_audience} onChange={e => set('target_audience', e.target.value)} />
          <div style={{ display: 'grid', gap: 6 }}>
            <div style={{ fontSize: 12, opacity: 0.9 }}>Targeting</div>
            <input placeholder="Age group (e.g., 18-24)" value={form.targeting_options.age_group} onChange={e => setNested('age_group', e.target.value)} />
            <input placeholder="Gender" value={form.targeting_options.gender || ''} onChange={e => setNested('gender', e.target.value)} />
            <input placeholder="Location" value={form.targeting_options.location || ''} onChange={e => setNested('location', e.target.value)} />
            <input placeholder="Interests" value={form.targeting_options.interests || ''} onChange={e => setNested('interests', e.target.value)} />
          </div>
          <input placeholder="USP" value={form.unique_selling_proposition} onChange={e => set('unique_selling_proposition', e.target.value)} />
          <input placeholder="Offer details" value={form.offer_details || ''} onChange={e => set('offer_details', e.target.value)} />
          <input placeholder="Budget range (e.g., $50-200/day)" value={form.budget_range} onChange={e => set('budget_range', e.target.value)} />
          <input placeholder="Campaign duration" value={form.campaign_duration || ''} onChange={e => set('campaign_duration', e.target.value)} />
          <input placeholder="Brand voice" value={form.brand_voice || ''} onChange={e => set('brand_voice', e.target.value)} />
        </div>
        <button onClick={run} disabled={loading} style={{ marginTop: 8 }}>{loading ? 'Generating…' : 'Generate'}</button>
        {error && <div style={{ marginTop: 8, color: '#c33', fontSize: 12 }}>{error}</div>}
      </div>
    );
  };

  useCopilotActionTyped({
    name: 'generateFacebookAdCopy',
    description: 'Generate ad copy (primary text) for Facebook ads',
    parameters: [
      { name: 'business_type', type: 'string', required: false },
      { name: 'product_service', type: 'string', required: false },
      { name: 'ad_objective', type: 'string', required: false },
      { name: 'ad_format', type: 'string', required: false },
      { name: 'target_audience', type: 'string', required: false }
    ],
    renderAndWaitForResponse: ({ args, respond }: any) => <AdCopyHITL args={args} respond={respond} />,
    handler: async (args: any) => {
      const payload = {
        business_type: args?.business_type,
        product_service: args?.product_service || 'Product X',
        ad_objective: args?.ad_objective || 'Conversions',
        ad_format: args?.ad_format || 'Single image',
        target_audience: args?.target_audience,
        targeting_options: { age_group: '18-24' },
        unique_selling_proposition: 'Fast, reliable, loved by users',
        budget_range: '$50-200/day'
      } as any;
      const res = await facebookWriterApi.adCopyGenerate(payload);
      const variations = {
        headline_variations: res?.ad_variations?.headline_variations || res?.data?.ad_variations?.headline_variations || [],
        primary_text_variations: res?.ad_variations?.primary_text_variations || res?.data?.ad_variations?.primary_text_variations || [],
        description_variations: res?.ad_variations?.description_variations || res?.data?.ad_variations?.description_variations || [],
        cta_variations: res?.ad_variations?.cta_variations || res?.data?.ad_variations?.cta_variations || []
      };
      window.dispatchEvent(new CustomEvent('fbwriter:adVariations', { detail: variations }));
      const primaryObj = res?.primary_ad_copy || res?.data?.primary_ad_copy;
      const message = primaryObj?.primary_text || primaryObj?.text || res?.content || res?.data?.content || 'Ad copy generated.';
      window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: `\n\n${message}` }));
      return { success: true, content: message };
    }
  });

  // Story generation
  const VALID_STORY_TYPES = ['Product showcase','Behind the scenes','User testimonial','Event promotion','Tutorial/How-to','Question/Poll','Announcement','Custom'];
  const VALID_STORY_TONES = ['Casual','Fun','Professional','Inspirational','Educational','Entertaining','Custom'];

  function mapStoryType(t?: string) {
    const s = (t || '').trim().toLowerCase();
    const exact = VALID_STORY_TYPES.find(v => v.toLowerCase() === s);
    if (exact) return exact;
    if (s.includes('behind')) return 'Behind the scenes';
    if (s.includes('testi')) return 'User testimonial';
    if (s.includes('event')) return 'Event promotion';
    if (s.includes('tutorial') || s.includes('how')) return 'Tutorial/How-to';
    if (s.includes('poll') || s.includes('question')) return 'Question/Poll';
    if (s.includes('announce')) return 'Announcement';
    return 'Product showcase';
  }
  function mapStoryTone(t?: string) {
    const s = (t || '').trim().toLowerCase();
    const exact = VALID_STORY_TONES.find(v => v.toLowerCase() === s);
    if (exact) return exact;
    if (s.includes('fun')) return 'Fun';
    if (s.includes('inspir')) return 'Inspirational';
    if (s.includes('educat')) return 'Educational';
    if (s.includes('entertain')) return 'Entertaining';
    if (s.includes('pro')) return 'Professional';
    return 'Casual';
  }

  const StoryHITL: React.FC<{ args: any; respond?: (data: any) => void }> = ({ args, respond }) => {
    const prefs = React.useMemo(() => readPrefs(), []);
    const [form, setForm] = React.useState({
      business_type: args?.business_type || prefs.business_type || 'SaaS',
      target_audience: args?.target_audience || prefs.target_audience || 'Marketing managers at SMEs',
      story_type: mapStoryType(args?.story_type) || 'Product showcase',
      story_tone: mapStoryTone(args?.story_tone) || 'Casual',
      include: args?.include || '',
      avoid: args?.avoid || '',
      // Advanced options
      use_hook: true,
      use_story: true,
      use_cta: true,
      use_question: true,
      use_emoji: true,
      use_hashtags: true,
      // Visual options
      visual_options: {
        background_type: args?.visual_options?.background_type || 'Solid color',
        background_image_prompt: args?.visual_options?.background_image_prompt || '',
        gradient_style: args?.visual_options?.gradient_style || '',
        text_overlay: args?.visual_options?.text_overlay ?? true,
        text_style: args?.visual_options?.text_style || '',
        text_color: args?.visual_options?.text_color || '',
        text_position: args?.visual_options?.text_position || '',
        stickers: args?.visual_options?.stickers ?? true,
        interactive_elements: args?.visual_options?.interactive_elements ?? true,
        interactive_types: args?.visual_options?.interactive_types || [],
        call_to_action: args?.visual_options?.call_to_action || ''
      }
    });
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const safeRespond = (d: any) => { try { if (typeof respond === 'function') respond(d); } catch {} };

    const run = async () => {
      try {
        setLoading(true);
        setError(null);

        // 1) Always try to generate an image via the new Facebook image endpoint (LinkedIn-style)
        let imageGenerated = false;
        try {
          const parts: string[] = [];
          if (form.story_type) parts.push(String(mapStoryType(form.story_type)));
          if (form.story_tone) parts.push(`${mapStoryTone(form.story_tone)} tone`);
          if (form.include) parts.push(`Include: ${form.include}`);
          if (form.avoid) parts.push(`Avoid: ${form.avoid}`);
          const prompt = (form.visual_options?.background_image_prompt || parts.join(', ')) || 'Facebook story visual';
          const imgRes = await facebookWriterApi.generateFacebookImageNew({ 
            prompt, 
            aspect_ratio: '9:16', 
            content_context: {
              content_type: 'story',
              topic: form.include || 'story',
              business_type: form.business_type || 'general'
            }
          });
          const images = imgRes?.images;
          if (Array.isArray(images) && images.length) {
            window.dispatchEvent(new CustomEvent('fbwriter:storyImages', { detail: images }));
            imageGenerated = true;
          } else if (imgRes && imgRes.error) {
            window.dispatchEvent(new CustomEvent('fbwriter:assistantMessage', { detail: { content: `Image generation failed: ${imgRes.error}` } }));
          }
        } catch (imgErr: any) {
          const msg = imgErr?.response?.data?.detail || imgErr?.message || 'Image generation failed';
          window.dispatchEvent(new CustomEvent('fbwriter:assistantMessage', { detail: { content: msg } }));
        }

        // 2) Always generate text as well (preserve existing behavior)
        const payload = {
          ...form,
          story_type: mapStoryType(form.story_type),
          story_tone: mapStoryTone(form.story_tone),
          visual_options: {
            ...form.visual_options,
            interactive_types: Array.isArray(form.visual_options?.interactive_types)
              ? form.visual_options?.interactive_types
              : []
          }
        } as any;
        const res = await facebookWriterApi.storyGenerate(payload);
        const content = res?.content || res?.data?.content;
        if (content) {
          window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: `\n\n${content}` }));
          logAssistant(content);
          safeRespond({ success: true, content, image: imageGenerated });
        } else {
          safeRespond({ success: true, message: imageGenerated ? 'Story image generated.' : 'Story generated.' });
        }
      } catch (e: any) {
        const msg = e?.response?.data?.detail || e?.message || 'Failed to generate story';
        setError(`${msg}`);
        safeRespond({ success: false, message: `${msg}` });
      } finally {
        setLoading(false);
      }
    };

    const set = (k: string, v: any) => setForm((prev: any) => ({ ...prev, [k]: v }));
    const setVisual = (k: string, v: any) => setForm((prev: any) => ({ ...prev, visual_options: { ...prev.visual_options, [k]: v } }));
    const parseInteractive = (s: string): string[] => s.split(',').map(x => x.trim()).filter(Boolean);
    return (
      <div style={{ padding: 12 }}>
        <div style={{ fontWeight: 600, marginBottom: 8 }}>Generate Story</div>
        <div style={{ display: 'grid', gap: 8 }}>
          <input placeholder="Business type" value={form.business_type} onChange={e => set('business_type', e.target.value)} />
          <input placeholder="Target audience" value={form.target_audience} onChange={e => set('target_audience', e.target.value)} />
          <input placeholder="Story type (e.g., Product showcase)" value={form.story_type} onChange={e => set('story_type', e.target.value)} />
          <input placeholder="Tone (e.g., Casual)" value={form.story_tone} onChange={e => set('story_tone', e.target.value)} />
          <input placeholder="Include" value={form.include} onChange={e => set('include', e.target.value)} />
          <input placeholder="Avoid" value={form.avoid} onChange={e => set('avoid', e.target.value)} />
          <div style={{ marginTop: 8, fontWeight: 600 }}>Advanced options</div>
          <label><input type="checkbox" checked={form.use_hook} onChange={e => set('use_hook', e.target.checked)} /> Hook</label>
          <label><input type="checkbox" checked={form.use_story} onChange={e => set('use_story', e.target.checked)} /> Narrative</label>
          <label><input type="checkbox" checked={form.use_cta} onChange={e => set('use_cta', e.target.checked)} /> Include CTA</label>
          <label><input type="checkbox" checked={form.use_question} onChange={e => set('use_question', e.target.checked)} /> Ask question</label>
          <label><input type="checkbox" checked={form.use_emoji} onChange={e => set('use_emoji', e.target.checked)} /> Emojis</label>
          <label><input type="checkbox" checked={form.use_hashtags} onChange={e => set('use_hashtags', e.target.checked)} /> Hashtags</label>

          <div style={{ marginTop: 8, fontWeight: 600 }}>Visual options</div>
          <input placeholder="Background type (Solid color, Gradient, Image, Video)" value={form.visual_options.background_type} onChange={e => setVisual('background_type', e.target.value)} />
          <input placeholder="Background image/video prompt (if applicable)" value={form.visual_options.background_image_prompt || ''} onChange={e => setVisual('background_image_prompt', e.target.value)} />
          <input placeholder="Gradient style" value={form.visual_options.gradient_style || ''} onChange={e => setVisual('gradient_style', e.target.value)} />
          <label><input type="checkbox" checked={!!form.visual_options.text_overlay} onChange={e => setVisual('text_overlay', e.target.checked)} /> Text overlay</label>
          <input placeholder="Text style" value={form.visual_options.text_style || ''} onChange={e => setVisual('text_style', e.target.value)} />
          <input placeholder="Text color" value={form.visual_options.text_color || ''} onChange={e => setVisual('text_color', e.target.value)} />
          <input placeholder="Text position (e.g., Top-Left)" value={form.visual_options.text_position || ''} onChange={e => setVisual('text_position', e.target.value)} />
          <label><input type="checkbox" checked={!!form.visual_options.stickers} onChange={e => setVisual('stickers', e.target.checked)} /> Stickers/Emojis</label>
          <label><input type="checkbox" checked={!!form.visual_options.interactive_elements} onChange={e => setVisual('interactive_elements', e.target.checked)} /> Interactive elements</label>
          <input placeholder="Interactive types (comma-separated: poll,quiz,slider,countdown)" value={(form.visual_options.interactive_types || []).join(', ')} onChange={e => setVisual('interactive_types', parseInteractive(e.target.value))} />
          <input placeholder="CTA overlay text" value={form.visual_options.call_to_action || ''} onChange={e => setVisual('call_to_action', e.target.value)} />
        </div>
        <button onClick={run} disabled={loading} style={{ marginTop: 8 }}>{loading ? 'Generating…' : 'Generate'}</button>
        {error && <div style={{ marginTop: 8, color: '#c33', fontSize: 12 }}>{error}</div>}
      </div>
    );
  };

  useCopilotActionTyped({
    name: 'generateFacebookStory',
    description: 'Generate a Facebook Story image',
    parameters: [
      { name: 'business_type', type: 'string', required: false },
      { name: 'target_audience', type: 'string', required: false },
      { name: 'story_type', type: 'string', required: false },
      { name: 'story_tone', type: 'string', required: false },
      { name: 'include', type: 'string', required: false },
      { name: 'avoid', type: 'string', required: false },
      // Advanced flags
      { name: 'use_hook', type: 'boolean', required: false },
      { name: 'use_story', type: 'boolean', required: false },
      { name: 'use_cta', type: 'boolean', required: false },
      { name: 'use_question', type: 'boolean', required: false },
      { name: 'use_emoji', type: 'boolean', required: false },
      { name: 'use_hashtags', type: 'boolean', required: false },
      // Visual options
      { name: 'visual_options.background_type', type: 'string', required: false },
      { name: 'visual_options.background_image_prompt', type: 'string', required: false },
      { name: 'visual_options.gradient_style', type: 'string', required: false },
      { name: 'visual_options.text_overlay', type: 'boolean', required: false },
      { name: 'visual_options.text_style', type: 'string', required: false },
      { name: 'visual_options.text_color', type: 'string', required: false },
      { name: 'visual_options.text_position', type: 'string', required: false },
      { name: 'visual_options.stickers', type: 'boolean', required: false },
      { name: 'visual_options.interactive_elements', type: 'boolean', required: false },
      { name: 'visual_options.interactive_types', type: 'array', required: false },
      { name: 'visual_options.call_to_action', type: 'string', required: false }
    ],
    renderAndWaitForResponse: ({ args, respond }: any) => <StoryHITL args={args} respond={respond} />,
    handler: async (args: any) => {
      // Build an image prompt
      const parts: string[] = [];
      if (args?.story_type) parts.push(String(args.story_type));
      if (args?.story_tone) parts.push(`${args.story_tone} tone`);
      if (args?.include) parts.push(`Include: ${args.include}`);
      if (args?.avoid) parts.push(`Avoid: ${args.avoid}`);
      const prompt = (args?.visual_options?.background_image_prompt || args?.topic || parts.join(', ')) || 'Facebook story visual';

      try {
        const health = await facebookWriterApi.health();
        if (!health?.image_providers?.available) {
          const msg = 'Image generation not configured. Please set GEMINI_API_KEY (or Nano Banana) in backend/.env and restart.';
          window.dispatchEvent(new CustomEvent('fbwriter:assistantMessage', { detail: { content: msg } }));
          return { success: false, message: msg };
        }
      } catch {}

      const res = await facebookWriterApi.generateImagenImages({ prompt, number_of_images: 1, aspect_ratio: '9:16' });
      const images = res?.images;
      if (Array.isArray(images) && images.length) {
        window.dispatchEvent(new CustomEvent('fbwriter:storyImages', { detail: images }));
        return { success: true, count: images.length };
      }
      return { success: false, message: 'No images generated. Check API keys/billing.' };
    }
  });

  // Image-enhanced generation actions
  useCopilotActionTyped({
    name: 'generateFacebookStoryWithImages',
    description: 'Generate a Facebook story with persona-aware images',
    parameters: [
      { name: 'business_type', type: 'string', required: false },
      { name: 'target_audience', type: 'string', required: false },
      { name: 'story_type', type: 'string', required: false },
      { name: 'story_tone', type: 'string', required: false },
      { name: 'background_image_prompt', type: 'string', required: false }
    ],
    handler: async (args: any) => {
      try {
        const payload = {
          business_type: args?.business_type || 'SaaS',
          target_audience: args?.target_audience || 'Marketing managers at SMEs',
          story_type: args?.story_type || 'Product showcase',
          story_tone: args?.story_tone || 'Professional',
          include: args?.include || '',
          avoid: args?.avoid || '',
          visual_options: {
            background_image_prompt: args?.background_image_prompt || '',
            background_type: 'Image',
            text_overlay: true,
            stickers: true,
            interactive_elements: true
          }
        };
        
        const res = await facebookWriterApi.storyGenerateWithImages(payload);
      const content = res?.content || res?.data?.content;
        const images = res?.images_base64 || res?.data?.images_base64 || [];
        
      if (content) {
          window.dispatchEvent(new CustomEvent('fbwriter:updateDraft', { detail: content }));
          
          if (images.length > 0) {
            window.dispatchEvent(new CustomEvent('fbwriter:showGeneratedImages', { 
              detail: { images, type: 'story' } 
            }));
          }
          
          return { success: true, content, images };
        }
        
        return { success: true, message: 'Story with images generated.' };
      } catch (e: any) {
        return { success: false, message: e?.message || 'Failed to generate story with images' };
      }
    }
  });

  useCopilotActionTyped({
    name: 'generateFacebookReelWithImages',
    description: 'Generate a Facebook reel with persona-aware thumbnail images',
    parameters: [
      { name: 'business_type', type: 'string', required: false },
      { name: 'target_audience', type: 'string', required: false },
      { name: 'reel_type', type: 'string', required: false },
      { name: 'reel_style', type: 'string', required: false },
      { name: 'topic', type: 'string', required: false }
    ],
    handler: async (args: any) => {
      try {
        const payload = {
          business_type: args?.business_type || 'SaaS',
          target_audience: args?.target_audience || 'Marketing managers at SMEs',
          reel_type: args?.reel_type || 'Product demonstration',
          reel_length: '30-60 seconds',
          reel_style: args?.reel_style || 'Fast-paced',
          topic: args?.topic || 'Feature walkthrough',
          include: args?.include || '',
          avoid: args?.avoid || '',
          music_preference: 'Trending'
        };
        
        const res = await facebookWriterApi.reelGenerateWithImages(payload);
        const script = res?.script || res?.data?.script;
        const thumbnails = res?.thumbnail_images || res?.data?.thumbnail_images || [];
        
        if (script) {
          window.dispatchEvent(new CustomEvent('fbwriter:updateDraft', { detail: script }));
          
          if (thumbnails.length > 0) {
            window.dispatchEvent(new CustomEvent('fbwriter:showGeneratedImages', { 
              detail: { images: thumbnails, type: 'reel' } 
            }));
          }
          
          return { success: true, content: script, thumbnails };
        }
        
        return { success: true, message: 'Reel with images generated.' };
      } catch (e: any) {
        return { success: false, message: e?.message || 'Failed to generate reel with images' };
      }
    }
  });

  useCopilotActionTyped({
    name: 'generateFacebookCarouselWithImages',
    description: 'Generate a Facebook carousel with persona-aware images for each slide',
    parameters: [
      { name: 'business_type', type: 'string', required: false },
      { name: 'target_audience', type: 'string', required: false },
      { name: 'carousel_type', type: 'string', required: false },
      { name: 'topic', type: 'string', required: false },
      { name: 'num_slides', type: 'number', required: false }
    ],
    handler: async (args: any) => {
      try {
        const payload = {
          business_type: args?.business_type || 'SaaS',
          target_audience: args?.target_audience || 'Marketing managers at SMEs',
          carousel_type: args?.carousel_type || 'Product showcase',
          topic: args?.topic || 'Feature breakdown',
          num_slides: args?.num_slides || 5,
          include_cta: true,
          cta_text: 'Learn More',
          include: args?.include || '',
          avoid: args?.avoid || ''
        };
        
        const res = await facebookWriterApi.carouselGenerateWithImages(payload);
        const mainCaption = res?.main_caption || res?.data?.main_caption;
        const slides = res?.slides || res?.data?.slides || [];
        
        if (mainCaption) {
          let content = mainCaption;
          if (slides.length > 0) {
            content += '\n\nCarousel Slides:';
            slides.forEach((slide: any, i: number) => {
              content += `\n${i + 1}. ${slide.title}: ${slide.content}`;
            });
          }
          
          window.dispatchEvent(new CustomEvent('fbwriter:updateDraft', { detail: content }));
          
          // Show carousel images
          const slideImages = slides.filter((slide: any) => slide.image_base64).map((slide: any) => slide.image_base64);
          if (slideImages.length > 0) {
            window.dispatchEvent(new CustomEvent('fbwriter:showGeneratedImages', { 
              detail: { images: slideImages, type: 'carousel' } 
            }));
          }
          
          return { success: true, content, slides };
        }
        
        return { success: true, message: 'Carousel with images generated.' };
      } catch (e: any) {
        return { success: false, message: e?.message || 'Failed to generate carousel with images' };
      }
    }
  });

  // Image generation action using Gemini API
  useCopilotActionTyped({
    name: 'generateFacebookStoryImage',
    description: 'Generate an image for Facebook Story using Gemini API based on story content and visual description',
    parameters: [
      { name: 'story_text', type: 'string', required: true },
      { name: 'visual_description', type: 'string', required: true },
      { name: 'background_color', type: 'string', required: false },
      { name: 'text_overlay', type: 'string', required: false },
      { name: 'emojis', type: 'string', required: false },
      { name: 'aspect_ratio', type: 'string', required: false }
    ],
    handler: async (args: any) => {
      try {
        const payload = {
          story_text: args?.story_text || '',
          visual_description: args?.visual_description || '',
          background_color: args?.background_color || 'PINK gradient',
          text_overlay: args?.text_overlay || '',
          emojis: args?.emojis || '',
          aspect_ratio: args?.aspect_ratio || '9:16' // Facebook Story format
        };

        const response = await facebookWriterApi.generateStoryImage(payload);
        
        return {
          success: true,
          message: 'Facebook Story image generated successfully using Gemini API',
          data: response
        };
      } catch (error) {
        return {
          success: false,
          message: `Failed to generate Facebook Story image: ${error}`,
          error: error
        };
      }
    }
  });

  // Facebook Publishing Action
  useCopilotActionTyped({
    name: 'publishFacebookPost',
    description: 'Publish the current Facebook post draft to a selected Facebook page',
    parameters: [
      { name: 'page_name', type: 'string', required: false, description: 'Name of the Facebook page to publish to (optional - will use default if not specified)' },
      { name: 'confirm', type: 'boolean', required: false, description: 'Whether to confirm before publishing (default: true)' }
    ],
    handler: async (args: any) => {
      try {
        console.log('🚀 Copilot: Starting Facebook post publication');
        
        // Get current draft content
        const currentDraft = document.querySelector('[data-testid="post-draft"]')?.textContent || 
                           document.querySelector('.post-draft')?.textContent || '';
        
        if (!currentDraft || currentDraft.trim().length === 0) {
          return {
            success: false,
            error: 'No post content found. Please generate a post first.',
            message: 'No post content available to publish'
          };
        }

        console.log('📝 Copilot: Found post content, checking Facebook connection');
        
        // Check Facebook connection status
        const connectionStatus = await facebookWriterApi.getFacebookConnectionStatus();
        
        if (!connectionStatus.connected) {
          return {
            success: false,
            error: 'Facebook not connected',
            message: 'Please connect your Facebook account first using the "Connect Facebook" button',
            action_required: 'connect_facebook'
          };
        }

        console.log('📘 Copilot: Facebook connected, fetching pages');
        
        // Get available pages
        const pages: Array<{ id: string; name: string }> = await facebookWriterApi.getFacebookPages();
        
        if (!pages || pages.length === 0) {
          return {
            success: false,
            error: 'No Facebook pages found',
            message: 'No Facebook pages available for publishing. Please ensure you have admin access to at least one Facebook page.',
            action_required: 'check_pages'
          };
        }

        // Find target page
        let targetPage = pages[0]; // Default to first page
        if (args?.page_name) {
          const foundPage = pages.find((page) => 
            page.name.toLowerCase().includes(args.page_name.toLowerCase())
          );
          if (foundPage) {
            targetPage = foundPage;
          } else {
            console.log(`⚠️ Copilot: Page "${args.page_name}" not found, using default page "${targetPage.name}"`);
          }
        }

        console.log(`📘 Copilot: Publishing to page "${targetPage.name}" (ID: ${targetPage.id})`);

        // Publish the post
        const result = await facebookWriterApi.publishFacebookPost({
          page_id: targetPage.id,
          message: currentDraft.trim()
        });

        if (result.success) {
          console.log(`✅ Copilot: Successfully published post ${result.post_id}`);
          
          // Dispatch success event to UI
          window.dispatchEvent(new CustomEvent('fbwriter:toast', { 
            detail: { 
              message: `Posted to ${targetPage.name} successfully!`, 
              type: 'success',
              action: result.permalink_url ? { label: 'View Post', url: result.permalink_url } : undefined
            }
          }));

          return {
            success: true,
            message: `Successfully published post to Facebook page "${targetPage.name}"`,
            post_id: result.post_id,
            page_name: targetPage.name,
            permalink_url: result.permalink_url,
            content_preview: currentDraft.substring(0, 100) + (currentDraft.length > 100 ? '...' : '')
          };
        } else {
          console.error(`❌ Copilot: Failed to publish post: ${result.error}`);
          return {
            success: false,
            error: result.error || 'Unknown publishing error',
            message: `Failed to publish post to Facebook: ${result.error}`,
            page_name: targetPage.name
          };
        }

      } catch (error: any) {
        console.error('❌ Copilot: Error in Facebook publishing action:', error);
        return {
          success: false,
          error: `Publishing failed: ${error.message}`,
          message: `Failed to publish to Facebook: ${error.message}`
        };
      }
    }
  });

  // Hashtag generation action
  useCopilotActionTyped({
    name: 'generateFacebookHashtags',
    description: 'Generate relevant hashtags for Facebook content',
    parameters: [
      { name: 'content_topic', type: 'string', required: false }
    ],
    renderAndWaitForResponse: ({ args, respond }: any) => <HashtagsHITL args={args} respond={respond} />,
    handler: async (args: any) => {
      try {
        const res = await facebookWriterApi.hashtagsGenerate({ content_topic: args?.content_topic || 'general content' });
        console.log('Hashtag generation response:', res);
        
        const hashtags = res?.hashtags || res?.data?.hashtags;
        if (Array.isArray(hashtags) && hashtags.length) {
          const line = hashtags.join(' ');
          window.dispatchEvent(new CustomEvent('fbwriter:appendDraft', { detail: `\n\n${line}` }));
          logAssistant(line);
          return { success: true, hashtags };
        } else {
          console.log('No hashtags found in response:', res);
          return { success: true, message: 'Hashtags generated.' };
        }
      } catch (e: any) {
        console.error('[FB Writer] hashtags.generate error:', e);
        const msg = e?.response?.data?.detail || e?.message || 'Failed to generate hashtags';
        return { success: false, message: msg };
      }
    }
  });

  return null;
};

export default RegisterFacebookActions;


