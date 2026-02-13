
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Mail, Send, Eye, Edit, Brain, Users, TrendingUp, Zap, Activity } from "lucide-react";
import { useNavigate } from "react-router-dom";

export const EmailCampaigns = () => {
  const navigate = useNavigate();
  
  const campaigns = [
    {
      name: "AI Tools Guest Posts",
      status: "active",
      sent: 45,
      opened: 28,
      replied: 12,
      prospects: 67,
      lastActivity: "2 hours ago"
    },
    {
      name: "Content Marketing Outreach",
      status: "paused",
      sent: 32,
      opened: 18,
      replied: 8,
      prospects: 89,
      lastActivity: "1 day ago"
    },
    {
      name: "SEO Expert Quotes",
      status: "draft",
      sent: 0,
      opened: 0,
      replied: 0,
      prospects: 23,
      lastActivity: "3 hours ago"
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-500";
      case "paused": return "bg-yellow-500";
      case "draft": return "bg-blue-500";
      default: return "bg-gray-500";
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <Card className="neural-glow">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Mail className="w-5 h-5 text-accent" />
              AI Email Campaigns
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                <Activity className="w-3 h-3 mr-1" />
                3 Campaigns
              </Badge>
              <Badge variant="outline" className="text-xs">
                <TrendingUp className="w-3 h-3 mr-1" />
                28% Reply Rate
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="campaigns" className="border-primary/20">
              <AccordionTrigger className="hover:no-underline">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-accent" />
                    <span>Active Email Campaigns</span>
                  </div>
                  <Badge variant="default" className="text-xs">
                    AI Powered
                  </Badge>
                </div>
              </AccordionTrigger>
              <AccordionContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {campaigns.map((campaign, index) => (
                    <motion.div
                      key={index}
                      className="p-4 rounded-lg glass-card border"
                      whileHover={{ scale: 1.02 }}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${getStatusColor(campaign.status)}`} />
                          <span className="font-medium text-sm">{campaign.name}</span>
                        </div>
                        <Badge variant="outline" className="text-xs capitalize">
                          {campaign.status}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3 mb-3">
                        <div className="text-center p-2 rounded bg-muted/30">
                          <div className="text-lg font-bold">{campaign.sent}</div>
                          <div className="text-xs text-muted-foreground">Sent</div>
                        </div>
                        <div className="text-center p-2 rounded bg-muted/30">
                          <div className="text-lg font-bold">{campaign.replied}</div>
                          <div className="text-xs text-muted-foreground">Replies</div>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
                        <span className="flex items-center gap-1">
                          <Users className="w-3 h-3" />
                          {campaign.prospects} prospects
                        </span>
                        <span className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" />
                          {campaign.opened > 0 ? Math.round((campaign.opened / campaign.sent) * 100) : 0}% open
                        </span>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button variant="ghost" size="sm" className="flex-1">
                          <Eye className="w-3 h-3 mr-1" />
                          View
                        </Button>
                        {campaign.status === "draft" ? (
                          <Button variant="ai" size="sm" className="flex-1">
                            <Send className="w-3 h-3 mr-1" />
                            Launch
                          </Button>
                        ) : (
                          <Button variant="neural" size="sm" className="flex-1">
                            <Edit className="w-3 h-3 mr-1" />
                            Edit
                          </Button>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
                
                <div className="flex gap-3">
                  <Button 
                    variant="ai" 
                    className="flex-1"
                    onClick={() => navigate("/new-campaign")}
                  >
                    <Brain className="w-4 h-4 mr-2" />
                    Generate AI Campaign
                  </Button>
                  <Button 
                    variant="neural" 
                    className="flex-1"
                    onClick={() => navigate("/new-campaign")}
                  >
                    <Mail className="w-4 h-4 mr-2" />
                    Create Custom Campaign
                  </Button>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>
    </motion.div>
  );
};
