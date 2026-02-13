
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { 
  Handshake, 
  CheckCircle, 
  Clock, 
  AlertTriangle, 
  Eye,
  MessageSquare,
  Link,
  Calendar,
  Hash,
  Reply,
  Lightbulb,
  Target,
  Brain,
  Users
} from "lucide-react";

export const CollaborationTracker = () => {
  const collaborations = [
    {
      domain: "techcrunch.com",
      contact: "Sarah Johnson",
      status: "in_progress",
      type: "Guest Post",
      deadline: "2024-01-15",
      lastUpdate: "Received draft outline",
      priority: "high",
      campaign: "AI Tools Guest Posts",
      keywords: ["AI content marketing", "automation tools"],
      lastReply: "Thanks for the detailed outline. We'd like to proceed with the guest post. Can you provide the full draft by next week?",
      aiInsight: "High engagement potential. Editor responded positively. Website analysis shows strong editorial standards and high-quality guest content."
    },
    {
      domain: "contentmarketing.org",
      contact: "Mike Chen",
      status: "review_needed",
      type: "Resource Link",
      deadline: "2024-01-20",
      lastUpdate: "Human review required",
      priority: "medium",
      campaign: "Content Marketing Outreach",
      keywords: ["content optimization", "SEO automation"],
      lastReply: "We're interested but need to review your content quality first. Please send some sample articles for our editorial team.",
      aiInsight: "Cautious but interested response. They have strict content guidelines. Previous successful placements suggest good conversion potential."
    },
    {
      domain: "aitrends.net",
      contact: "Lisa Rodriguez",
      status: "completed",
      type: "Case Study",
      deadline: "2024-01-10",
      lastUpdate: "Published successfully",
      priority: "low",
      campaign: "AI Tools Case Studies",
      keywords: ["machine learning", "digital marketing AI"],
      lastReply: "Case study is now live! Here's the link: aitrends.net/case-studies/alwrity-ai-success. Great collaboration!",
      aiInsight: "Successful completion. High-quality backlink secured from DA 65 domain. Strong referral traffic potential. Consider for future partnerships."
    },
    {
      domain: "marketingland.com",
      contact: "David Park",
      status: "negotiating",
      type: "Expert Quote",
      deadline: "2024-01-25",
      lastUpdate: "Discussing terms",
      priority: "high",
      campaign: "Expert Authority Building",
      keywords: ["marketing automation", "AI tools"],
      lastReply: "We can feature you as an expert, but we'll need you to provide insights on 3 different topics. Are you available for a 30-min interview?",
      aiInsight: "Opportunity for thought leadership positioning. High-authority domain (DA 88). Interview format suggests potential for multiple quote placements."
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed": return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "in_progress": return <Clock className="w-4 h-4 text-blue-500" />;
      case "review_needed": return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case "negotiating": return <MessageSquare className="w-4 h-4 text-purple-500" />;
      default: return <Handshake className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "bg-red-500";
      case "medium": return "bg-yellow-500";
      case "low": return "bg-green-500";
      default: return "bg-gray-500";
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <Card className="quantum-glow">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-primary" />
              Collaboration Tracker
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs neural-pulse">
                <Target className="w-3 h-3 mr-1" />
                4 Active
              </Badge>
              <Badge variant="outline" className="text-xs">
                <Brain className="w-3 h-3 mr-1" />
                AI Reviews
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="collaborations" className="border-primary/20">
              <AccordionTrigger className="hover:no-underline">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-primary" />
                    <span>Active Collaborations</span>
                  </div>
                  <Badge variant="default" className="text-xs">
                    Human-in-Loop
                  </Badge>
                </div>
              </AccordionTrigger>
              <AccordionContent className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {collaborations.map((collab, index) => (
                    <motion.div
                      key={index}
                      className="p-6 rounded-xl neural-glow bg-gradient-to-br from-background/80 via-background/60 to-background/40 border border-primary/20 backdrop-blur-sm"
                      whileHover={{ scale: 1.02, y: -2 }}
                      transition={{ type: "spring", stiffness: 300, damping: 20 }}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-lg bg-primary/10 quantum-glow">
                            {getStatusIcon(collab.status)}
                          </div>
                          <div>
                            <span className="font-semibold text-base text-foreground">{collab.domain}</span>
                            <div className="text-xs text-muted-foreground">{collab.contact}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${getPriorityColor(collab.priority)} quantum-pulse`} />
                          <Badge variant="secondary" className="text-xs font-medium">
                            {collab.type}
                          </Badge>
                        </div>
                      </div>

                      <div className="mb-4">
                        <div className="text-xs text-muted-foreground mb-2">Campaign:</div>
                        <Badge variant="outline" className="text-xs">
                          {collab.campaign}
                        </Badge>
                      </div>

                      <div className="mb-4">
                        <div className="text-xs text-muted-foreground mb-2">Target Keywords:</div>
                        <div className="flex flex-wrap gap-1">
                          {collab.keywords.map((keyword, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              <Hash className="w-2 h-2 mr-1" />
                              {keyword}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div className="bg-gradient-to-r from-muted/50 to-muted/30 rounded-lg p-3 mb-4 border border-border/50">
                        <div className="flex items-center gap-2 mb-2">
                          <Reply className="w-3 h-3 text-muted-foreground" />
                          <div className="text-xs text-muted-foreground font-medium">Last Reply:</div>
                        </div>
                        <div className="text-sm italic">"{collab.lastReply}"</div>
                      </div>

                      <div className="bg-gradient-to-r from-primary/5 to-accent/5 rounded-lg p-3 mb-4 border border-primary/10">
                        <div className="flex items-center gap-2 mb-2">
                          <Lightbulb className="w-3 h-3 text-primary" />
                          <div className="text-xs text-primary font-medium">AI Insight:</div>
                        </div>
                        <div className="text-sm text-foreground">{collab.aiInsight}</div>
                      </div>
                      
                      <div className="space-y-3 mb-4">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Deadline:</span>
                          <span className="flex items-center gap-2 font-medium">
                            <Calendar className="w-4 h-4 text-primary" />
                            {collab.deadline}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex gap-3">
                        <Button variant="outline" size="sm" className="flex-1 neural-glow">
                          <Eye className="w-4 h-4 mr-2" />
                          Details
                        </Button>
                        {collab.status === "review_needed" && (
                          <Button variant="ai" size="sm" className="flex-1">
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Review
                          </Button>
                        )}
                        {collab.status === "completed" && (
                          <Button variant="secondary" size="sm" className="flex-1">
                            <Link className="w-4 h-4 mr-2" />
                            View Link
                          </Button>
                        )}
                        {collab.status === "negotiating" && (
                          <Button variant="neural" size="sm" className="flex-1">
                            <MessageSquare className="w-4 h-4 mr-2" />
                            Respond
                          </Button>
                        )}
                        {collab.status === "in_progress" && (
                          <Button variant="outline" size="sm" className="flex-1">
                            <Clock className="w-4 h-4 mr-2" />
                            Track
                          </Button>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
                
                <div className="p-6 rounded-xl bg-gradient-neural border border-primary/40 neural-glow quantum-glow">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold mb-2 text-lg">AI Analysis Summary</h4>
                      <p className="text-sm text-muted-foreground">
                        2 collaborations need human review • 1 high-priority deadline approaching
                      </p>
                      <div className="flex gap-4 mt-3 text-xs">
                        <span className="text-green-400">✓ 1 Completed</span>
                        <span className="text-blue-400">⏳ 1 In Progress</span>
                        <span className="text-yellow-400">⚠ 1 Review Needed</span>
                        <span className="text-purple-400">💬 1 Negotiating</span>
                      </div>
                    </div>
                    <Button variant="ai" size="lg" className="quantum-pulse">
                      <AlertTriangle className="w-5 h-5 mr-2" />
                      Review Queue
                    </Button>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>
    </motion.div>
  );
};
