
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Search, Zap, TrendingUp, Plus, Brain, Target, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";

export const KeywordResearch = () => {
  const navigate = useNavigate();
  
  const keywords = [
    { term: "AI content marketing", volume: 12500, difficulty: "Medium", opportunities: 45 },
    { term: "SEO automation tools", volume: 8900, difficulty: "High", opportunities: 23 },
    { term: "Content optimization", volume: 15600, difficulty: "Low", opportunities: 67 },
    { term: "Digital marketing AI", volume: 9800, difficulty: "Medium", opportunities: 34 }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <Card className="neural-glow h-full">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Search className="w-5 h-5 text-primary" />
              AI Keyword Research
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                <Target className="w-3 h-3 mr-1" />
                4 Active
              </Badge>
              <Badge variant="outline" className="text-xs">
                <Sparkles className="w-3 h-3 mr-1" />
                169 Opportunities
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="research" className="border-primary/20">
              <AccordionTrigger className="hover:no-underline">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <Brain className="w-4 h-4 text-primary" />
                    <span>AI Research & Suggestions</span>
                  </div>
                  <Badge variant="default" className="text-xs">
                    Live
                  </Badge>
                </div>
              </AccordionTrigger>
              <AccordionContent className="space-y-4">
                <div className="flex gap-2">
                  <Input 
                    placeholder="Enter keywords or domain..."
                    className="bg-muted/50 border-primary/20"
                  />
                  <Button 
                    variant="ai" 
                    size="sm"
                    onClick={() => navigate("/new-campaign")}
                  >
                    <Brain className="w-4 h-4" />
                  </Button>
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-sm">Active Keywords</h4>
                    <Button variant="ghost" size="sm">
                      <Plus className="w-4 h-4 mr-1" />
                      Add
                    </Button>
                  </div>
                  
                  {keywords.map((keyword, index) => (
                    <motion.div
                      key={index}
                      className="p-3 rounded-lg glass-card border"
                      whileHover={{ scale: 1.02 }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-sm">{keyword.term}</span>
                        <Badge 
                          variant={keyword.difficulty === "Low" ? "secondary" : 
                                 keyword.difficulty === "Medium" ? "outline" : "destructive"}
                          className="text-xs"
                        >
                          {keyword.difficulty}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Vol: {keyword.volume.toLocaleString()}</span>
                        <span className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" />
                          {keyword.opportunities} ops
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
                
                <Button 
                  variant="neural" 
                  className="w-full"
                  onClick={() => navigate("/new-campaign")}
                >
                  <Zap className="w-4 h-4 mr-2" />
                  Start New Research Campaign
                </Button>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>
    </motion.div>
  );
};
