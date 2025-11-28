import React, { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { BlogResearchResponse, ResearchProvider } from "../../services/blogWriterApi";
import { podcastApi } from "../../services/podcastApi";
import {
  CreateProjectPayload,
  Fact,
  Job,
  Knobs,
  Line,
  PodcastAnalysis,
  PodcastEstimate,
  Query,
  RenderJobResult,
  Research,
  Scene,
  Script,
} from "./types";

/* ================= UI PRIMITIVES ================= */

const Card: React.FC<{ className?: string; children?: React.ReactNode; "aria-label"?: string }> = ({
  children,
  className = "",
  ["aria-label"]: ariaLabel,
}) => (
  <section
    role="region"
    aria-label={ariaLabel}
    className={`backdrop-blur-xl bg-[#071022]/80 border border-white/10 text-white rounded-2xl p-5 shadow-2xl ${className}`}
  >
    {children}
  </section>
);

const PrimaryButton: React.FC<{
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  ariaLabel?: string;
}> = ({ children, onClick, disabled = false, ariaLabel }) => (
  <motion.button
    whileHover={{ scale: disabled ? 1 : 1.02 }}
    whileTap={{ scale: disabled ? 1 : 0.97 }}
    onClick={onClick}
    disabled={disabled}
    aria-label={ariaLabel}
    className={`inline-flex items-center gap-2 px-4 py-2 rounded-md font-medium shadow ${
      disabled ? "bg-gray-400 text-gray-800 cursor-not-allowed" : "bg-gradient-to-r from-indigo-500 to-blue-600 text-white"
    }`}
  >
    {children}
  </motion.button>
);

const SecondaryButton: React.FC<{ children: React.ReactNode; onClick?: () => void; ariaLabel?: string }> = ({
  children,
  onClick,
  ariaLabel,
}) => (
  <motion.button
    whileHover={{ scale: 1.02 }}
    whileTap={{ scale: 0.97 }}
    onClick={onClick}
    aria-label={ariaLabel}
    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-sm border bg-transparent"
  >
    {children}
  </motion.button>
);

const Input: React.FC<React.InputHTMLAttributes<HTMLInputElement>> = (props) => (
  <input
    {...props}
    className={`mt-1 block w-full rounded-md border border-white/20 bg-white/6 text-white placeholder-white/40 p-2 ${
      props.className ?? ""
    }`}
    style={{ backdropFilter: "blur(6px)" }}
  />
);

const Label: React.FC<{ htmlFor?: string; children: React.ReactNode }> = ({ htmlFor, children }) => (
  <label htmlFor={htmlFor} className="block text-sm font-medium text-white/90">
    {children}
  </label>
);

/* ================= Helpers ================= */

const DEFAULT_KNOBS: Knobs = {
  voice_emotion: "neutral",
  voice_speed: 1,
  resolution: "720p",
  scene_length_target: 45,
  sample_rate: 24000,
  bitrate: "standard",
};

const getSceneVoiceEmotion = (knobs: Knobs) => knobs.voice_emotion || "neutral";

const announceError = (setAnnouncement: (msg: string) => void, error: unknown) => {
  const message = error instanceof Error ? error.message : "Unexpected error";
  setAnnouncement(message);
};

/* ================= CreateModal ================= */

const CreateModal: React.FC<{
  onCreate: (payload: CreateProjectPayload) => void;
  open: boolean;
  defaultKnobs: Knobs;
}> = ({ onCreate, open, defaultKnobs }) => {
  const [idea, setIdea] = useState("");
  const [url, setUrl] = useState("");
  const [speakers, setSpeakers] = useState<number>(1);
  const [duration, setDuration] = useState<number>(10);
  const [budgetCap, setBudgetCap] = useState<number>(50);
  const [voiceFile, setVoiceFile] = useState<File | null>(null);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [knobs, setKnobs] = useState<Knobs>({ ...defaultKnobs });

  const submit = () => {
    if (!idea && !url) return;
    onCreate({
      ideaOrUrl: idea || url,
      speakers,
      duration,
      knobs,
      budgetCap,
      files: { voiceFile, avatarFile },
    });
  };

  if (!open) return null;

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="fixed inset-0 bg-black/60 backdrop-blur-md z-40" />
      <motion.aside
        initial={{ opacity: 0, y: 24, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ type: "spring", stiffness: 280, damping: 30 }}
        className="fixed left-1/2 top-12 transform -translate-x-1/2 z-50 w-[min(1100px,95%)] max-h-[85vh] overflow-auto"
      >
        <Card className="glass-panel border border-white/10 overflow-hidden">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-purple-300 to-blue-200">
                Create episode
              </h3>
              <p className="text-sm text-gray-300 mt-1">Enter a short idea or paste a blog URL. We&apos;ll analyze and suggest defaults.</p>
            </div>
            <PrimaryButton onClick={submit} ariaLabel="Analyze and continue">
              Analyze & Continue
            </PrimaryButton>
          </div>

          <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <div>
                <Label htmlFor="idea_input">Idea (one-line)</Label>
                <Input id="idea_input" placeholder="Write a short idea or paste a blog URL" value={idea} onChange={(e) => setIdea(e.target.value)} />
                <p className="text-xs text-gray-400 mt-1">One sentence is enough — AI will expand it into an outline.</p>
              </div>

              <div>
                <Label htmlFor="url_input">Or Blog URL</Label>
                <Input id="url_input" placeholder="https://yourblog.com/post" value={url} onChange={(e) => setUrl(e.target.value)} />
                <p className="text-xs text-gray-400 mt-1">Providing a URL lets the AI ground the script in article facts.</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="speakers_select">Speakers</Label>
                  <select
                    id="speakers_select"
                    aria-label="Number of speakers"
                    value={speakers}
                    onChange={(e) => setSpeakers(Number(e.target.value))}
                    className="mt-1 block w-full rounded-md border border-white/10 bg-transparent p-2"
                  >
                    <option value={1}>1 (single)</option>
                    <option value={2}>2 (dialog)</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="duration_input">Duration (mins)</Label>
                  <Input id="duration_input" type="number" value={duration} onChange={(e) => setDuration(Number(e.target.value))} />
                </div>
              </div>

              <div>
                <Label htmlFor="budget_input">Budget cap (USD)</Label>
                <Input id="budget_input" type="number" value={budgetCap} onChange={(e) => setBudgetCap(Number(e.target.value))} />
                <p className="text-xs text-gray-400 mt-1">We&apos;ll prevent renders that exceed this cap.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Voice sample (optional)</Label>
                  <input aria-label="Upload voice sample" type="file" accept="audio/*" onChange={(e) => setVoiceFile(e.target.files?.[0] ?? null)} className="mt-2" />
                  <p className="text-xs text-gray-400 mt-1">10–30s clean wav/mp3 recommended.</p>
                </div>
                <div>
                  <Label>Avatar image (optional)</Label>
                  <input aria-label="Upload avatar image" type="file" accept="image/*" onChange={(e) => setAvatarFile(e.target.files?.[0] ?? null)} className="mt-2" />
                  <p className="text-xs text-gray-400 mt-1">Square image works best.</p>
                </div>
              </div>
            </div>

            <aside className="space-y-4">
              <div className="p-4 bg-gradient-to-br from-indigo-600/30 to-blue-400/20 rounded-lg border border-white/10">
                <h4 className="text-sm font-semibold text-white/90">Quick estimate</h4>
                <div className="mt-3 text-sm text-gray-200">Estimate updates after analysis.</div>
              </div>

              <div className="p-4 rounded-lg border border-white/6 bg-white/3">
                <h5 className="text-sm font-medium">Production defaults</h5>
                <div className="mt-2 text-xs text-gray-300">Voice emotion</div>
                <div className="mt-1 flex items-center gap-2">
                  {["enthusiastic", "neutral", "calm"].map((emotion) => (
                    <button
                      key={emotion}
                      onClick={() => setKnobs({ ...knobs, voice_emotion: emotion })}
                      className={`px-2 py-1 rounded ${
                        knobs.voice_emotion === emotion ? "bg-indigo-600/30" : "bg-white/5"
                      } text-sm`}
                    >
                      {emotion}
                    </button>
                  ))}
                </div>

                <div className="mt-3 text-xs text-gray-300">Audio quality</div>
                <div className="mt-1 flex items-center gap-2">
                  {["preview", "standard", "hd"].map((tier) => (
                    <button
                      key={tier}
                      onClick={() => setKnobs({ ...knobs, bitrate: tier })}
                      className={`px-2 py-1 rounded ${knobs.bitrate === tier ? "bg-indigo-600/30" : "bg-white/5"} text-sm`}
                    >
                      {tier.toUpperCase()}
                    </button>
                  ))}
                </div>

                <div className="mt-3">
                  <SecondaryButton onClick={() => setKnobs({ ...defaultKnobs })}>Reset defaults</SecondaryButton>
                </div>
              </div>

              <div className="p-4 rounded-lg border border-white/6 bg-white/3">
                <h5 className="text-sm font-medium">Privacy & consent</h5>
                <p className="mt-2 text-xs text-gray-300">We require explicit consent before creating voice clones.</p>
              </div>
            </aside>
          </div>

          <div className="mt-6 flex items-center justify-between">
            <div className="text-xs text-gray-400">By continuing you agree to our processing terms for AI-generated voices and avatars.</div>
            <div className="flex items-center gap-3">
              <SecondaryButton
                onClick={() => {
                  setIdea("");
                  setUrl("");
                  setSpeakers(1);
                  setDuration(10);
                  setBudgetCap(50);
                  setVoiceFile(null);
                  setAvatarFile(null);
                  setKnobs({ ...defaultKnobs });
                }}
              >
                Reset
              </SecondaryButton>
              <PrimaryButton onClick={submit}>Analyze & Continue</PrimaryButton>
            </div>
          </div>
        </Card>
      </motion.aside>
    </div>
  );
};

/* ================= FactCard & AnalysisPanel ================= */

const FactCard: React.FC<{ fact: Fact }> = ({ fact }) => {
  const hostname = useMemo(() => {
    try {
      return new URL(fact.url).hostname;
    } catch {
      return fact.url;
    }
  }, [fact.url]);
  return (
    <motion.div whileHover={{ y: -4 }} className="rounded-lg border border-white/6 bg-white/4 p-3">
      <div className="text-sm text-gray-100">{fact.quote}</div>
      <div className="text-xs text-gray-300 mt-2">
        Source:{" "}
        <a className="text-indigo-300 underline" href={fact.url} target="_blank" rel="noreferrer">
          {hostname || "source"}
        </a>
      </div>
      <div className="text-xs text-gray-400 mt-1">
        Date: {fact.date} • Confidence: {(fact.confidence * 100).toFixed(0)}%
      </div>
    </motion.div>
  );
};

const AnalysisPanel: React.FC<{ analysis: PodcastAnalysis | null; onRegenerate?: () => void }> = ({ analysis, onRegenerate }) => {
  if (!analysis) return null;
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.28 }}>
      <Card className="lg:col-span-2" aria-label="analysis-panel">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-purple-300 to-blue-200">AI Analysis</h3>
            <p className="text-sm text-gray-300 mt-1">Defaults derived from WaveSpeed + story writer setup.</p>
          </div>
          <div>
            <SecondaryButton onClick={onRegenerate}>Regenerate</SecondaryButton>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium text-gray-100">Audience</h4>
            <p className="mt-1 text-sm text-gray-200">{analysis.audience}</p>

            <h4 className="font-medium mt-3 text-gray-100">Content Type</h4>
            <p className="mt-1 text-sm text-gray-200">{analysis.contentType}</p>

            <h4 className="font-medium mt-3 text-gray-100">Top Keywords</h4>
            <ul className="mt-1 list-disc ml-5 text-sm text-gray-200">
              {analysis.topKeywords.map((k) => (
                <li key={k}>{k}</li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-medium text-gray-100">Suggested Outlines</h4>
            <ul className="mt-1 text-sm text-gray-200">
              {analysis.suggestedOutlines.map((o) => (
                <li key={o.id} className="mb-2">
                  <strong>{o.title}:</strong> {o.segments.join(" • ")}
                </li>
              ))}
            </ul>

            <h4 className="font-medium mt-3 text-gray-100">Title Suggestions</h4>
            <div className="mt-2 flex gap-2 flex-wrap">
              {analysis.titleSuggestions.map((t) => (
                <button key={t} className="px-3 py-1 bg-white/6 border border-white/6 rounded text-sm hover:bg-white/10">
                  {t}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};

/* ================= Script Editor ================= */

const LineEditor: React.FC<{
  line: Line;
  onChange: (l: Line) => void;
  onPreview: (text: string) => Promise<{ ok: boolean; message: string; audioUrl?: string }>;
}> = ({ line, onChange, onPreview }) => {
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(line.text);
  useEffect(() => setText(line.text), [line.text]);

  return (
    <motion.div whileHover={{ y: -3 }} className="p-3 border rounded-lg bg-white/5">
      <div className="flex items-start gap-4">
        <div className="flex-1">
          <div className="text-sm font-semibold text-gray-100">{line.speaker}</div>
          {editing ? (
            <textarea value={text} onChange={(e) => setText(e.target.value)} className="mt-2 w-full p-2 rounded bg-black/5 text-sm" rows={3} />
          ) : (
            <div className="mt-2 text-sm text-gray-200">{line.text}</div>
          )}
          <div className="mt-2 text-xs text-gray-400">Facts: {line.usedFactIds?.length ? line.usedFactIds.join(", ") : "None"}</div>
        </div>

        <div className="flex flex-col gap-2">
          <button
            className="px-3 py-1 rounded bg-white/6 text-sm"
            onClick={() => {
              if (editing) {
                onChange({ ...line, text });
              }
              setEditing(!editing);
            }}
          >
            {editing ? "Save" : "Edit"}
          </button>

          <PrimaryButton
            onClick={async () => {
              const res = await onPreview(line.text);
              if (res.audioUrl) window.open(res.audioUrl, "_blank");
              else alert(res.message);
            }}
          >
            Preview TTS
          </PrimaryButton>
        </div>
      </div>
    </motion.div>
  );
};

const SceneEditor: React.FC<{
  scene: Scene;
  onUpdateScene: (s: Scene) => void;
  onApprove: (id: string) => Promise<void>;
  onPreviewLine: (text: string) => Promise<{ ok: boolean; message: string; audioUrl?: string }>;
}> = ({ scene, onUpdateScene, onApprove, onPreviewLine }) => {
  const updateLine = (updatedLine: Line) => {
    const updated = { ...scene, lines: scene.lines.map((l) => (l.id === updatedLine.id ? updatedLine : l)) };
    onUpdateScene(updated);
  };

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-lg font-semibold text-gray-100">{scene.title}</h4>
          <div className="text-xs text-gray-400">Duration: {scene.duration}s</div>
        </div>
        <div className="flex items-center gap-2">
          <div className={`text-sm px-2 py-1 rounded ${scene.approved ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}>
            {scene.approved ? "Approved" : "Not approved"}
          </div>
          <PrimaryButton
            onClick={async () => {
              await onApprove(scene.id);
              onUpdateScene({ ...scene, approved: true });
            }}
          >
            Approve Scene
          </PrimaryButton>
        </div>
      </div>

      <div className="mt-3 space-y-3">
        {scene.lines.map((line) => (
          <LineEditor key={line.id} line={line} onChange={updateLine} onPreview={(text) => onPreviewLine(text)} />
        ))}
      </div>
    </Card>
  );
};

const ScriptEditor: React.FC<{
  projectId: string;
  idea: string;
  research: Research | null;
  rawResearch: BlogResearchResponse | null;
  knobs: Knobs;
  speakers: number;
  durationMinutes: number;
  onBackToResearch: () => void;
  onProceedToRendering: (script: Script) => void;
}> = ({ projectId, idea, research, rawResearch, knobs, speakers, durationMinutes, onBackToResearch, onProceedToRendering }) => {
  const [script, setScript] = useState<Script | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    podcastApi
      .generateScript({
        projectId,
        idea,
        research: rawResearch,
        knobs,
        speakers,
        durationMinutes,
      })
      .then((res) => {
        if (mounted) {
          setScript(res);
          setError(null);
        }
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to generate script");
      })
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [projectId, rawResearch, idea, knobs, speakers, durationMinutes]);

  const updateScene = (updated: Scene) => {
    if (!script) return;
    setScript({ ...script, scenes: script.scenes.map((s) => (s.id === updated.id ? updated : s)) });
  };

  const approveScene = async (sceneId: string) => {
    try {
      await podcastApi.approveScene({ projectId, sceneId });
      setScript((prev) =>
        prev
          ? {
              ...prev,
              scenes: prev.scenes.map((s) => (s.id === sceneId ? { ...s, approved: true } : s)),
            }
          : prev
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to approve scene";
      setError(message);
      throw err;
    }
  };

  const allApproved = script && script.scenes.every((s) => s.approved);

  return (
    <div className="mt-6">
      <div className="flex items-center gap-3 mb-4">
        <button className="text-sm text-gray-400" onClick={onBackToResearch}>
          ← Back to research
        </button>
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-purple-300 to-blue-200">Script Editor</h2>
      </div>

      {loading && <div className="p-3 bg-yellow-50 rounded text-black">Generating script...</div>}
      {error && <div className="p-3 bg-red-100 text-red-900 rounded">{error}</div>}

      {script && (
        <div className="space-y-4">
          <div className="p-3 bg-white/5 rounded border">
            <div className="text-sm text-gray-300">Each scene must be approved before rendering.</div>
          </div>

          {script.scenes.map((scene) => (
            <motion.div key={scene.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
              <SceneEditor scene={scene} onUpdateScene={updateScene} onApprove={approveScene} onPreviewLine={(text) => podcastApi.previewLine(text)} />
            </motion.div>
          ))}

          <div className="mt-4 p-4 bg-white/5 rounded flex items-center justify-between">
            <div>
              <div className="text-sm">All scenes approved: {allApproved ? "Yes" : "No"}</div>
              <div className="text-xs text-gray-400">Rendering enabled after all scenes are approved.</div>
            </div>
            <div>
              <PrimaryButton onClick={() => script && onProceedToRendering(script)} disabled={!allApproved}>
                Proceed to Rendering
              </PrimaryButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/* ================= Render Queue ================= */

const RenderQueue: React.FC<{
  projectId: string;
  script: Script;
  knobs: Knobs;
  onBack: () => void;
}> = ({ projectId, script, knobs, onBack }) => {
  const [jobs, setJobs] = useState<Job[]>(
    script.scenes.map((s) => ({ sceneId: s.id, title: s.title, status: "idle", progress: 0, previewUrl: null, finalUrl: null, jobId: null }))
  );
  const [rendering, setRendering] = useState<string | null>(null);

  const getScene = (sceneId: string) => script.scenes.find((s) => s.id === sceneId);

  const runRender = async (sceneId: string, mode: "preview" | "full") => {
    const scene = getScene(sceneId);
    if (!scene) return;
    setRendering(sceneId);
    setJobs((list) =>
      list.map((job) =>
        job.sceneId === sceneId
          ? { ...job, status: mode === "preview" ? "previewing" : "running", progress: mode === "preview" ? 25 : 40 }
          : job
      )
    );
    try {
      const result: RenderJobResult = await podcastApi.renderSceneAudio({
        scene,
        voiceId: "Wise_Woman",
        emotion: getSceneVoiceEmotion(knobs),
        speed: knobs.voice_speed,
      });
      setJobs((list) =>
        list.map((job) =>
          job.sceneId === sceneId
            ? {
                ...job,
                status: "completed",
                progress: 100,
                previewUrl: mode === "preview" ? result.audioUrl : job.previewUrl,
                finalUrl: mode === "full" ? result.audioUrl : job.finalUrl,
              }
            : job
        )
      );
      if (mode === "preview") window.open(result.audioUrl, "_blank");
    } catch (error) {
      setJobs((list) =>
        list.map((job) => (job.sceneId === sceneId ? { ...job, status: "failed", progress: 0 } : job))
      );
    } finally {
      setRendering(null);
    }
  };

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-4">
        <button className="text-sm text-gray-400" onClick={onBack}>
          ← Back to script
        </button>
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-purple-300 to-blue-200">Render Queue</h2>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {jobs.map((job) => (
          <Card key={job.sceneId} className="p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-md bg-white/5 flex items-center justify-center text-gray-200 font-semibold">
                {job.title
                  .split(" ")
                  .slice(0, 2)
                  .map((s) => s[0])
                  .join("")}
              </div>
              <div>
                <div className="font-medium text-gray-100">{job.title}</div>
                <div className="text-xs text-gray-400">Scene: {job.sceneId}</div>
                {job.finalUrl && (
                  <div className="text-sm mt-1">
                    Final:{" "}
                    <a className="text-indigo-300 underline" href={job.finalUrl} target="_blank" rel="noreferrer">
                      Download
                    </a>
                  </div>
                )}
              </div>
            </div>

            <div className="flex-1">
              <div className="flex items-center justify-between gap-4">
                <div className="text-sm">
                  Status: <strong className="capitalize">{job.status}</strong>
                </div>
                <div className="text-xs text-gray-400">Progress: {job.progress}%</div>
              </div>

              <div className="w-full bg-white/7 rounded overflow-hidden h-2 mt-2">
                <div className="h-2 bg-gradient-to-r from-indigo-400 to-blue-400" style={{ width: `${job.progress}%` }} />
              </div>

              <div className="mt-3 flex items-center gap-2 justify-end flex-wrap">
                {job.status === "idle" && (
                  <>
                    <SecondaryButton onClick={() => runRender(job.sceneId, "preview")}>Preview</SecondaryButton>
                    <PrimaryButton onClick={() => runRender(job.sceneId, "full")} disabled={rendering === job.sceneId}>
                      Start Full Render
                    </PrimaryButton>
                  </>
                )}
                {job.status === "completed" && job.previewUrl && (
                  <PrimaryButton onClick={() => window.open(job.previewUrl || job.finalUrl || "#", "_blank")}>
                    Listen
                  </PrimaryButton>
                )}
                {job.status === "failed" && (
                  <button onClick={() => runRender(job.sceneId, "full")} className="px-3 py-1 rounded-md bg-yellow-500 text-black text-sm">
                    Retry
                  </button>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="flex justify-end mt-4">
        <SecondaryButton onClick={onBack}>Done</SecondaryButton>
      </div>
    </div>
  );
};

/* ================= Dashboard ================= */

const PodcastDashboard: React.FC = () => {
  const [project, setProject] = useState<{ id: string; idea: string; duration: number; speakers: number } | null>(null);
  const [analysis, setAnalysis] = useState<PodcastAnalysis | null>(null);
  const [queries, setQueries] = useState<Query[]>([]);
  const [selectedQueries, setSelectedQueries] = useState<Set<string>>(new Set());
  const [research, setResearch] = useState<Research | null>(null);
  const [rawResearch, setRawResearch] = useState<BlogResearchResponse | null>(null);
  const [estimate, setEstimate] = useState<PodcastEstimate | null>(null);
  const [loading, setLoading] = useState(false);
  const [announcement, setAnnouncement] = useState("");
  const [showScriptEditor, setShowScriptEditor] = useState(false);
  const [showRenderQueue, setShowRenderQueue] = useState(false);
  const [scriptData, setScriptData] = useState<Script | null>(null);
  const [knobsState, setKnobsState] = useState<Knobs>(DEFAULT_KNOBS);
  const [researchProvider, setResearchProvider] = useState<ResearchProvider>("google");

  useEffect(() => {
    if (announcement) {
      const t = setTimeout(() => setAnnouncement(""), 4000);
      return () => clearTimeout(t);
    }
    return undefined;
  }, [announcement]);

  const handleCreate = async (payload: CreateProjectPayload) => {
    try {
      setLoading(true);
      setAnnouncement("Analyzing your idea — AI suggestions incoming");
      const result = await podcastApi.createProject(payload);
      setProject({ id: result.projectId, idea: payload.ideaOrUrl, duration: payload.duration, speakers: payload.speakers });
      setAnalysis(result.analysis);
      setEstimate(result.estimate);
      setQueries(result.queries);
      setSelectedQueries(new Set(result.queries.map((q) => q.id)));
      setKnobsState(payload.knobs);
      setAnnouncement("Analysis complete");
    } catch (error) {
      announceError(setAnnouncement, error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunResearch = async () => {
    if (!project) {
      setAnnouncement("Create a project first.");
      return;
    }
    try {
      setLoading(true);
      setAnnouncement("Running grounded research — fetching sources");
      const approvedQueries = queries.filter((q) => selectedQueries.has(q.id));
      const { research: mapped, raw } = await podcastApi.runResearch({
        projectId: project.id,
        topic: project.idea,
        approvedQueries,
        provider: researchProvider,
      });
      setResearch(mapped);
      setRawResearch(raw);
      setAnnouncement("Research ready — review fact cards");
    } catch (error) {
      announceError(setAnnouncement, error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateScript = () => {
    if (!project || !research) {
      setAnnouncement("Project or research missing — cannot generate script");
      return;
    }
    setScriptData(null);
    setShowScriptEditor(true);
  };

  const handleProceedToRendering = (script: Script) => {
    setScriptData(script);
    setShowRenderQueue(true);
    setShowScriptEditor(false);
  };

  const toggleQuery = (id: string) => {
    setSelectedQueries((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <main className="p-6 max-w-7xl mx-auto">
      <header className="flex items-center justify-between mb-6 flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold">Alwrity — AI Podcast Maker</h1>
          <p className="text-sm text-gray-400">Create grounded episodes with editable scripts and WaveSpeed renders.</p>
        </div>
        <div className="flex items-center gap-3">
          <SecondaryButton onClick={() => window.open("/docs", "_blank")}>Docs</SecondaryButton>
          <PrimaryButton onClick={() => window.location.reload()}>New Episode</PrimaryButton>
        </div>
      </header>

      {announcement && (
        <div className="mb-4 rounded bg-blue-50 text-blue-900 px-4 py-2 border border-blue-200 shadow">{announcement}</div>
      )}

      {loading && <div className="p-3 mb-4 bg-yellow-50 text-yellow-900 rounded border border-yellow-200">Working... please wait</div>}

      {!project && <CreateModal open onCreate={handleCreate} defaultKnobs={DEFAULT_KNOBS} />}

      <div className="space-y-6">
        {analysis && !showScriptEditor && !showRenderQueue && <AnalysisPanel analysis={analysis} onRegenerate={() => setAnalysis({ ...analysis })} />}

        {estimate && !showScriptEditor && !showRenderQueue && (
          <Card className="mt-4" aria-label="estimate">
            <h5 className="font-semibold">Estimated cost</h5>
            <div className="mt-2 text-sm text-gray-200">Total estimate: ${estimate.total}</div>
            <div className="text-xs text-gray-400 mt-1">
              TTS ${estimate.ttsCost} • Avatars ${estimate.avatarCost} • Research ${estimate.researchCost}
            </div>
          </Card>
        )}

        {queries.length > 0 && !showScriptEditor && !showRenderQueue && (
          <div>
            <Card className="mt-4 space-y-4">
              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <h5 className="font-semibold">Queries</h5>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">Provider:</span>
                  <select
                    value={researchProvider}
                    onChange={(e) => setResearchProvider(e.target.value as ResearchProvider)}
                    className="bg-black/30 border border-white/10 rounded px-3 py-1 text-sm"
                  >
                    <option value="google">Google Grounding</option>
                    <option value="exa">Exa Neural Search</option>
                  </select>
                </div>
              </div>
              <div className="grid gap-3">
                {queries.map((q) => (
                  <label key={q.id} className="flex items-start gap-3 text-sm text-gray-200 border border-white/10 rounded-lg p-3">
                    <input
                      type="checkbox"
                      checked={selectedQueries.has(q.id)}
                      onChange={() => toggleQuery(q.id)}
                      className="mt-1"
                    />
                    <div>
                      <div>{q.query}</div>
                      <div className="text-xs text-gray-400">{q.rationale}</div>
                    </div>
                  </label>
                ))}
              </div>
              <div className="flex justify-end">
                <PrimaryButton onClick={handleRunResearch}>Run research</PrimaryButton>
              </div>
            </Card>
          </div>
        )}

        {research && !showScriptEditor && !showRenderQueue && (
          <div className="space-y-4">
            <Card className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Research summary</h3>
                <PrimaryButton onClick={handleGenerateScript}>Generate Script</PrimaryButton>
              </div>
              <p className="text-sm text-gray-200">{research.summary}</p>
              {research.factCards.length > 0 && (
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {research.factCards.map((fact) => (
                    <FactCard key={fact.id} fact={fact} />
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}

        {showScriptEditor && project && (
          <ScriptEditor
            projectId={project.id}
            idea={project.idea}
            research={research}
            rawResearch={rawResearch}
            knobs={knobsState}
            speakers={project.speakers}
            durationMinutes={project.duration}
            onBackToResearch={() => setShowScriptEditor(false)}
            onProceedToRendering={(s) => handleProceedToRendering(s)}
          />
        )}

        {showRenderQueue && project && scriptData && (
          <RenderQueue
            projectId={project.id}
            script={scriptData}
            knobs={knobsState}
            onBack={() => {
              setShowRenderQueue(false);
              setShowScriptEditor(true);
            }}
          />
        )}
      </div>
    </main>
  );
};

export default PodcastDashboard;

