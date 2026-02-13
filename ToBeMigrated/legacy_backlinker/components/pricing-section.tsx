import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Sparkles, Shield, Zap } from "lucide-react";

export const PricingSection = () => {
  const plans = [
    {
      name: "Starter",
      price: "$0",
      period: "/mo",
      highlight: "Get started with AI backlinking",
      features: [
        "50 opportunity scans/mo",
        "AI email drafts (basic)",
        "Manual send",
        "Basic analytics"
      ],
      cta: "Start Free",
      variant: "neural"
    },
    {
      name: "Pro",
      price: "$49",
      period: "/mo",
      highlight: "Scale campaigns with automation",
      features: [
        "5k scans + batch processing",
        "AI personalization + follow-ups",
        "SMTP/Gmail integration",
        "Response analysis"
      ],
      cta: "Upgrade",
      variant: "ai"
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "",
      highlight: "Advanced controls & SLAs",
      features: [
        "Unlimited scans",
        "Domain authority scoring",
        "Human-in-the-loop workflow",
        "SSO, Audit logs, SLAs"
      ],
      cta: "Contact Sales",
      variant: "outline"
    }
  ];

  return (
    <section id="pricing" className="py-20 px-4 relative scroll-mt-24">
      <div className="container mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Pricing for <span className="bg-gradient-primary bg-clip-text text-transparent">Every Stage</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Start free. Scale with AI automation and enterprise controls when you need them.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.4, delay: i * 0.1 }}>
              <Card className={`h-full neural-glow ${i === 1 ? 'shadow-neural' : ''}`}>
                <CardHeader>
                  <div className="flex items-center justify-between mb-2">
                    <CardTitle className="text-2xl">{plan.name}</CardTitle>
                    {i === 1 ? <Sparkles className="w-5 h-5 text-primary" /> : null}
                  </div>
                  <div className="flex items-end gap-1">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    <span className="text-muted-foreground mb-1">{plan.period}</span>
                  </div>
                  <div className="text-sm text-muted-foreground mt-2">{plan.highlight}</div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((f, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-primary mt-0.5" />
                        <span className="text-sm">{f}</span>
                      </li>
                    ))}
                  </ul>
                  <div className="flex items-center gap-3">
                    <Button variant={plan.variant as any} className="flex-1">
                      {plan.cta}
                    </Button>
                    {i === 2 ? <Shield className="w-5 h-5 text-accent" /> : <Zap className="w-5 h-5 text-secondary" />}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
