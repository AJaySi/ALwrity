import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, XCircle, Brain, Mail, Globe, Network, BarChart3, UserCheck } from "lucide-react";

export const ComparisonSection = () => {
  const manual = [
    "Manual Google searches, endless tabs",
    "Copy-paste emails scraped by hand",
    "Generic outreach with low replies",
    "No domain authority prioritization",
    "Spreadsheet chaos, hard to track",
    "Slow follow-ups and missed windows"
  ];

  const ai = [
    "AI web research finds and refines prospects",
    "Auto-scrapes verified contacts and roles",
    "Personalized AI emails for each prospect",
    "DA ranking + semantic relevance scoring",
    "Integrated sending + response intelligence",
    "Human-in-the-loop reviews where it matters"
  ];

  return (
    <section id="comparison" className="py-20 px-4 relative scroll-mt-24">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            From Manual Grind to <span className="bg-gradient-primary bg-clip-text text-transparent">AI-First Backlinking</span>
          </h2>
          <p className="text-muted-foreground max-w-3xl mx-auto">
            ALwrity Backlinker revolutionizes traditional backlinking by automating research, outreach, and analysis with powerful AI.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Manual */}
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.4 }}>
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="w-5 h-5 text-muted-foreground" />
                  Traditional Manual Backlinking
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {manual.map((item, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <XCircle className="w-4 h-4 text-destructive mt-0.5" />
                      <span className="text-sm text-muted-foreground">{item}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>

          {/* AI */}
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.4, delay: 0.1 }}>
            <Card className="h-full neural-glow shadow-neural">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5 text-primary" />
                  ALwrity AI-First Backlinker
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {ai.map((item, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary mt-0.5" />
                      <span className="text-sm">{item}</span>
                    </li>
                  ))}
                </ul>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                  {[
                    { icon: Network, label: "Prospects refined by AI" },
                    { icon: Mail, label: "Personalized outreach at scale" },
                    { icon: BarChart3, label: "Replies analyzed for collabs" }
                  ].map((k, i) => (
                    <div key={i} className="p-4 rounded-lg glass-card border flex items-center gap-2">
                      <k.icon className="w-4 h-4 text-accent" />
                      <span className="text-sm">{k.label}</span>
                    </div>
                  ))}
                </div>
                <div className="text-xs text-muted-foreground mt-3">Includes human-in-the-loop reviews for final send and approvals.</div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
