import { useState } from "react";
import { motion } from "framer-motion";
import { Navigation } from "@/components/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { 
  Search, 
  Brain, 
  Target, 
  Sparkles, 
  Plus,
  ArrowRight,
  Zap,
  Globe,
  Mail,
  Users,
  CheckCircle,
  Clock,
  Loader2
} from "lucide-react";
import { toast } from "@/hooks/use-toast";

const NewCampaign = () => {
  const [keywords, setKeywords] = useState("");
  const [targetDomain, setTargetDomain] = useState("");
  const [isResearchModalOpen, setIsResearchModalOpen] = useState(false);
  const [researchProgress, setResearchProgress] = useState(0);
  const [currentResearchStep, setCurrentResearchStep] = useState("");
  const [campaignName, setCampaignName] = useState("");

  const suggestedKeywords = [
    "AI content marketing",
    "Machine learning SEO",
    "Automated link building",
    "AI-powered marketing tools",
    "Content optimization software",
    "Digital marketing automation"
  ];

  const researchSteps = [
    "Analyzing your keywords with AI...",
    "Searching web for relevant prospects...",
    "Evaluating domain authority rankings...",
    "Scraping contact information...",
    "Reading prospect websites and blogs...",
    "Identifying content collaboration opportunities...",
    "Generating personalized email templates...",
    "Preparing campaign dashboard..."
  ];

  const startAIResearch = async () => {
    if (!keywords.trim() || !targetDomain.trim()) {
      toast({
        title: "Missing Information",
        description: "Please enter both keywords and target domain to start AI research.",
        variant: "destructive"
      });
      return;
    }

    setIsResearchModalOpen(true);
    setResearchProgress(0);

    // Simulate AI research process
    for (let i = 0; i < researchSteps.length; i++) {
      setCurrentResearchStep(researchSteps[i]);
      await new Promise(resolve => setTimeout(resolve, 2000));
      setResearchProgress(((i + 1) / researchSteps.length) * 100);
    }

    // After completion, redirect to email templates
    setTimeout(() => {
      setIsResearchModalOpen(false);
      toast({
        title: "AI Research Complete!",
        description: "Found 24 high-quality prospects. Ready to generate personalized emails.",
      });
    }, 1000);
  };

  const addKeyword = (keyword: string) => {
    if (!keywords.includes(keyword)) {
      setKeywords(prev => prev ? `${prev}, ${keyword}` : keyword);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-bg">
      <Navigation />
      <div className="pt-16">
        <div className="container mx-auto px-4 py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-4xl font-bold bg-gradient-text bg-clip-text text-transparent mb-4">
              Create New AI Campaign
            </h1>
            <p className="text-muted-foreground text-lg">
              Let ALwrity's AI revolutionize your backlinking strategy with intelligent prospect research and personalized outreach.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            {/* Main Campaign Setup */}
            <div className="xl:col-span-2 space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card className="neural-glow">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Search className="w-5 h-5 text-primary" />
                      AI Keyword Research & Target Setup
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="target-domain">Target Domain</Label>
                      <Input
                        id="target-domain"
                        placeholder="e.g., mycompany.com"
                        value={targetDomain}
                        onChange={(e) => setTargetDomain(e.target.value)}
                        className="neural-glow"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="keywords">Primary Keywords</Label>
                      <Textarea
                        id="keywords"
                        placeholder="Enter your target keywords (comma-separated)"
                        value={keywords}
                        onChange={(e) => setKeywords(e.target.value)}
                        className="neural-glow min-h-[100px]"
                      />
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Brain className="w-4 h-4 text-primary" />
                        <span className="text-sm font-medium">AI Keyword Suggestions</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {suggestedKeywords.map((keyword, index) => (
                          <motion.div
                            key={index}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <Badge
                              variant="outline"
                              className="cursor-pointer hover:bg-primary/10 transition-colors"
                              onClick={() => addKeyword(keyword)}
                            >
                              <Plus className="w-3 h-3 mr-1" />
                              {keyword}
                            </Badge>
                          </motion.div>
                        ))}
                      </div>
                    </div>

                    <Button
                      onClick={startAIResearch}
                      size="lg"
                      className="w-full neural-glow quantum-pulse"
                      disabled={!keywords.trim() || !targetDomain.trim()}
                    >
                      <Sparkles className="w-5 h-5 mr-2" />
                      Start AI Research & Prospect Discovery
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card className="neural-glow">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="w-5 h-5 text-primary" />
                      Campaign Configuration
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="campaign-name">Campaign Name</Label>
                      <Input
                        id="campaign-name"
                        placeholder="e.g., Q1 AI Content Partnerships"
                        value={campaignName}
                        onChange={(e) => setCampaignName(e.target.value)}
                        className="neural-glow"
                      />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            {/* AI Workflow Preview */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="space-y-6"
            >
              <Card className="neural-glow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-primary" />
                    AI Workflow Preview
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {[
                    { icon: Globe, title: "Web Research", desc: "AI analyzes 1000+ prospects" },
                    { icon: Brain, title: "Content Analysis", desc: "Reads websites & blogs" },
                    { icon: Mail, title: "Email Generation", desc: "Personalized outreach" },
                    { icon: Users, title: "Collaboration Tracking", desc: "Human-in-loop reviews" }
                  ].map((step, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 rounded-lg bg-gradient-to-r from-primary/5 to-accent/5">
                      <div className="p-2 rounded-lg bg-primary/10 quantum-glow">
                        <step.icon className="w-4 h-4 text-primary" />
                      </div>
                      <div>
                        <div className="font-medium text-sm">{step.title}</div>
                        <div className="text-xs text-muted-foreground">{step.desc}</div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className="neural-glow bg-gradient-neural border-primary/40">
                <CardContent className="p-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary mb-1">10x</div>
                    <div className="text-sm text-muted-foreground">Faster than manual outreach</div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>

      {/* AI Research Progress Modal */}
      <Dialog open={isResearchModalOpen} onOpenChange={() => {}}>
        <DialogContent className="neural-glow max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary animate-pulse" />
              AI Research in Progress
            </DialogTitle>
            <DialogDescription>
              ALwrity is analyzing prospects and generating personalized outreach strategies
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6 py-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Progress</span>
                <span>{Math.round(researchProgress)}%</span>
              </div>
              <Progress value={researchProgress} className="neural-glow" />
            </div>

            <div className="flex items-center gap-3 p-4 rounded-lg bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20">
              <Loader2 className="w-5 h-5 text-primary animate-spin" />
              <div>
                <div className="font-medium text-sm">{currentResearchStep}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  This may take a few minutes for comprehensive analysis
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="p-3 rounded-lg bg-background/50">
                <div className="text-lg font-bold text-primary">24</div>
                <div className="text-xs text-muted-foreground">Prospects Found</div>
              </div>
              <div className="p-3 rounded-lg bg-background/50">
                <div className="text-lg font-bold text-accent">18</div>
                <div className="text-xs text-muted-foreground">Emails Ready</div>
              </div>
            </div>

            {researchProgress === 100 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center p-4 rounded-lg bg-green-500/10 border border-green-500/20"
              >
                <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
                <div className="font-medium text-green-400">Research Complete!</div>
                <div className="text-xs text-muted-foreground">Redirecting to email templates...</div>
              </motion.div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default NewCampaign;