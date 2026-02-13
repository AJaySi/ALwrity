import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  Brain, 
  Search, 
  Mail, 
  BarChart, 
  Users, 
  Zap,
  Globe,
  Target,
  Shield
} from "lucide-react";

export const FeaturesSection = () => {
  const features = [
    {
      icon: Search,
      title: "Intelligent Discovery",
      description: "AI-powered web scraping finds high-quality guest posting opportunities across the web",
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      icon: Brain,
      title: "Neural Personalization",
      description: "Advanced AI crafts personalized outreach emails tailored to each target website",
      gradient: "from-purple-500 to-pink-500"
    },
    {
      icon: Mail,
      title: "Automated Outreach",
      description: "Streamlined email campaigns with follow-up automation and response tracking",
      gradient: "from-green-500 to-emerald-500"
    },
    {
      icon: BarChart,
      title: "Advanced Analytics",
      description: "Real-time performance metrics, open rates, and backlink success tracking",
      gradient: "from-orange-500 to-red-500"
    },
    {
      icon: Users,
      title: "Lead Management",
      description: "Comprehensive contact database with status tracking and relationship management",
      gradient: "from-indigo-500 to-blue-500"
    },
    {
      icon: Zap,
      title: "Batch Processing",
      description: "Handle multiple keywords and campaigns simultaneously for maximum efficiency",
      gradient: "from-yellow-500 to-orange-500"
    },
    {
      icon: Globe,
      title: "Global Reach",
      description: "Find opportunities across multiple languages and geographic regions",
      gradient: "from-teal-500 to-cyan-500"
    },
    {
      icon: Target,
      title: "Smart Targeting",
      description: "AI algorithms identify the most promising prospects based on domain authority and relevance",
      gradient: "from-rose-500 to-pink-500"
    },
    {
      icon: Shield,
      title: "Safe & Compliant",
      description: "Built-in safeguards ensure ethical outreach practices and compliance with email regulations",
      gradient: "from-slate-500 to-gray-500"
    }
  ];

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
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <section id="features" className="py-20 px-4 relative scroll-mt-24">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 20% 50%, hsl(var(--primary)) 0%, transparent 50%), 
                           radial-gradient(circle at 80% 20%, hsl(var(--secondary)) 0%, transparent 50%),
                           radial-gradient(circle at 40% 80%, hsl(var(--accent)) 0%, transparent 50%)`
        }} />
      </div>

      <div className="container mx-auto max-w-7xl relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Powered by{" "}
            <span className="bg-gradient-primary bg-clip-text text-transparent">
              Advanced AI
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Every feature is enhanced with machine learning algorithms to maximize your backlinking success
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              whileHover={{ y: -5 }}
              transition={{ duration: 0.2 }}
            >
              <Card className="neural-glow h-full group hover:shadow-neural transition-all duration-300">
                <CardHeader>
                  <div className="flex items-center gap-3 mb-2">
                    <div className={`p-3 rounded-xl bg-gradient-to-r ${feature.gradient} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      <feature.icon className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <CardTitle className="text-xl group-hover:text-primary transition-colors duration-300">
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-center mt-16"
        >
          <div className="max-w-2xl mx-auto p-8 rounded-2xl glass-card border">
            <h3 className="text-2xl font-bold mb-4">
              Ready to Transform Your Link Building?
            </h3>
            <p className="text-muted-foreground mb-6">
              Join thousands of marketers using AI to build high-quality backlinks at scale
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 bg-gradient-primary text-primary-foreground rounded-lg font-semibold shadow-glow hover:shadow-neural transition-all duration-300"
              >
                Start Free Trial
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-3 neural-glow text-foreground rounded-lg font-semibold hover:bg-muted/50 transition-all duration-300"
              >
                Book Demo
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};