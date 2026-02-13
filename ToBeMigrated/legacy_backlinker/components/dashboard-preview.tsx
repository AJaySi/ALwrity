import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Search, 
  Mail, 
  TrendingUp, 
  Users, 
  Globe, 
  Zap,
  Eye,
  Send,
  CheckCircle,
  Clock
} from "lucide-react";

export const DashboardPreview = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <section id="dashboard" className="py-20 px-4 scroll-mt-24">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            AI-Driven{" "}
            <span className="bg-gradient-primary bg-clip-text text-transparent">
              Workflow
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Experience the power of automated backlinking with our intelligent dashboard
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          {/* Keyword Research Card */}
          <motion.div variants={itemVariants}>
            <Card className="neural-glow h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="w-5 h-5 text-primary" />
                  Keyword Discovery
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="relative">
                  <Input 
                    placeholder="Enter target keywords..."
                    className="bg-muted/50 border-primary/20"
                  />
                  <Button variant="ai" size="sm" className="absolute right-1 top-1">
                    <Zap className="w-4 h-4" />
                  </Button>
                </div>
                <div className="space-y-2">
                  {["AI tools", "content marketing", "SEO strategies"].map((keyword, index) => (
                    <div key={index} className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                      <span className="text-sm">{keyword}</span>
                      <Badge variant="secondary" className="text-xs">
                        {Math.floor(Math.random() * 500) + 100} ops
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Opportunities Card */}
          <motion.div variants={itemVariants}>
            <Card className="neural-glow h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="w-5 h-5 text-secondary" />
                  Found Opportunities
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { site: "TechBlog.com", da: 85, status: "pending" },
                  { site: "AIInsights.org", da: 72, status: "contacted" },
                  { site: "MarketingPro.net", da: 68, status: "replied" }
                ].map((opp, index) => (
                  <div key={index} className="p-3 rounded-lg glass-card border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-sm">{opp.site}</span>
                      <Badge variant="outline" className="text-xs">
                        DA {opp.da}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      {opp.status === "pending" && <Clock className="w-3 h-3 text-yellow-500" />}
                      {opp.status === "contacted" && <Send className="w-3 h-3 text-blue-500" />}
                      {opp.status === "replied" && <CheckCircle className="w-3 h-3 text-green-500" />}
                      <span className="text-xs capitalize text-muted-foreground">{opp.status}</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          {/* Email Campaign Card */}
          <motion.div variants={itemVariants}>
            <Card className="neural-glow h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-accent" />
                  AI Outreach
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-3 rounded-lg bg-muted/20 border">
                  <div className="text-xs text-muted-foreground mb-1">AI Generated Subject</div>
                  <div className="text-sm font-medium">Guest Post Collaboration Opportunity</div>
                </div>
                <div className="p-3 rounded-lg bg-muted/20 border">
                  <div className="text-xs text-muted-foreground mb-2">Personalized Content</div>
                  <div className="text-sm leading-relaxed">
                    "Hi Sarah, I noticed your recent article on AI automation was excellent. 
                    I'd love to contribute a piece on..."
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="neural" size="sm" className="flex-1">
                    <Eye className="w-4 h-4 mr-1" />
                    Preview
                  </Button>
                  <Button variant="ai" size="sm" className="flex-1">
                    <Send className="w-4 h-4 mr-1" />
                    Send
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Analytics Card - Full Width */}
          <motion.div variants={itemVariants} className="lg:col-span-3">
            <Card className="neural-glow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-primary" />
                  Campaign Analytics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {[
                    { label: "Emails Sent", value: "247", icon: Send, color: "text-blue-500" },
                    { label: "Responses", value: "89", icon: Mail, color: "text-green-500" },
                    { label: "Backlinks", value: "34", icon: CheckCircle, color: "text-purple-500" },
                    { label: "Success Rate", value: "36%", icon: TrendingUp, color: "text-accent" }
                  ].map((stat, index) => (
                    <motion.div 
                      key={index}
                      className="text-center p-4 rounded-lg glass-card"
                      whileHover={{ scale: 1.05 }}
                      transition={{ duration: 0.2 }}
                    >
                      <stat.icon className={`w-8 h-8 mx-auto mb-2 ${stat.color}`} />
                      <div className="text-2xl font-bold">{stat.value}</div>
                      <div className="text-sm text-muted-foreground">{stat.label}</div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};