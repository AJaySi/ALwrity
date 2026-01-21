
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Brain, Zap, Plus, Settings } from "lucide-react";

export const DashboardHeader = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card/50 backdrop-blur-xl border-b border-primary/20"
    >
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-gradient-primary neural-glow">
              <Brain className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">AI Backlinking Dashboard</h1>
              <p className="text-muted-foreground">Automated lead generation & outreach campaigns</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="neural" size="sm">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
            <Button variant="ai" size="sm">
              <Plus className="w-4 h-4 mr-2" />
              New Campaign
            </Button>
            <Button variant="hero" size="sm">
              <Zap className="w-4 h-4 mr-2" />
              AI Boost
            </Button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
