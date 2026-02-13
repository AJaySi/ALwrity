
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Globe, Brain, CheckCircle, Clock, AlertCircle, Eye, Users, BarChart3 } from "lucide-react";

export const ProspectAnalysis = () => {
  const prospects = [
    {
      domain: "techcrunch.com",
      da: 94,
      status: "analyzed",
      opportunity: "Guest Post",
      confidence: 92,
      contact: "editor@techcrunch.com"
    },
    {
      domain: "contentmarketing.org",
      da: 78,
      status: "pending",
      opportunity: "Resource Link",
      confidence: 85,
      contact: "info@contentmarketing.org"
    },
    {
      domain: "aitrends.net",
      da: 65,
      status: "reviewing",
      opportunity: "Case Study",
      confidence: 78,
      contact: "submissions@aitrends.net"
    },
    {
      domain: "marketingland.com",
      da: 88,
      status: "analyzed",
      opportunity: "Expert Quote",
      confidence: 88,
      contact: "news@marketingland.com"
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "analyzed": return <CheckCircle className="w-3 h-3 text-green-500" />;
      case "pending": return <Clock className="w-3 h-3 text-yellow-500" />;
      case "reviewing": return <AlertCircle className="w-3 h-3 text-blue-500" />;
      default: return <Globe className="w-3 h-3" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <Card className="neural-glow h-full">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-secondary" />
              AI Prospect Analysis
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                <Users className="w-3 h-3 mr-1" />
                4 Analyzed
              </Badge>
              <Badge variant="outline" className="text-xs">
                <BarChart3 className="w-3 h-3 mr-1" />
                86% Avg Score
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="prospects" className="border-primary/20">
              <AccordionTrigger className="hover:no-underline">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-secondary" />
                    <span>Refined Prospects</span>
                  </div>
                  <Badge variant="default" className="text-xs">
                    AI Scored
                  </Badge>
                </div>
              </AccordionTrigger>
              <AccordionContent className="space-y-4">
                <div className="space-y-3">
                  {prospects.map((prospect, index) => (
                    <motion.div
                      key={index}
                      className="p-3 rounded-lg glass-card border"
                      whileHover={{ scale: 1.02 }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(prospect.status)}
                          <span className="font-medium text-sm">{prospect.domain}</span>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          DA {prospect.da}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-2 mb-2 text-xs">
                        <div>
                          <span className="text-muted-foreground">Opportunity:</span>
                          <div className="font-medium">{prospect.opportunity}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">AI Score:</span>
                          <div className="font-medium text-primary">{prospect.confidence}%</div>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">
                          {prospect.contact}
                        </span>
                        <Button variant="ghost" size="sm">
                          <Eye className="w-3 h-3" />
                        </Button>
                      </div>
                    </motion.div>
                  ))}
                </div>
                
                <Button variant="ai" className="w-full">
                  <Brain className="w-4 h-4 mr-2" />
                  Analyze New Prospects
                </Button>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>
    </motion.div>
  );
};
