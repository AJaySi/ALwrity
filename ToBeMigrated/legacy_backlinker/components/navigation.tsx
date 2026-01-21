import { useState } from "react";
import { motion } from "framer-motion";
import { Brain } from "lucide-react";
import { Button } from "@/components/ui/button";

export const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed top-0 left-0 right-0 z-50 bg-card/80 backdrop-blur-xl border-b border-primary/20"
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <motion.div 
            className="flex items-center gap-3"
            whileHover={{ scale: 1.05 }}
          >
            <div className="p-2 rounded-lg bg-gradient-primary neural-glow">
              <Brain className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              ALwrity Backlinker
            </span>
          </motion.div>

          <div className="hidden md:flex items-center space-x-8">
            <a href="/#features" className="nav-link">Features</a>
            <a href="/#dashboard" className="nav-link">Demo</a>
            <a href="/#comparison" className="nav-link">Compare</a>
            <a href="/#pricing" className="nav-link">Pricing</a>
            <a href="/dashboard" className="nav-link">Dashboard</a>
            <a href="/new-campaign" className="nav-link">New Campaign</a>
          </div>

          <div className="md:hidden">
            <Button variant="outline" size="icon" onClick={() => setIsOpen(!isOpen)}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="lucide lucide-menu"
              >
                <line x1="4" x2="20" y1="12" y2="12" />
                <line x1="4" x2="20" y1="6" y2="6" />
                <line x1="4" x2="20" y1="18" y2="18" />
              </svg>
            </Button>
          </div>
        </div>
      </div>

      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="md:hidden absolute top-full left-0 right-0 bg-card shadow-md rounded-b-md border-b border-primary/20"
        >
          <div className="container mx-auto p-4 flex flex-col gap-4">
            <a href="/#features" className="nav-link block">Features</a>
            <a href="/#dashboard" className="nav-link block">Demo</a>
            <a href="/#comparison" className="nav-link block">Compare</a>
            <a href="/#pricing" className="nav-link block">Pricing</a>
            <a href="/dashboard" className="nav-link block">Dashboard</a>
            <a href="/new-campaign" className="nav-link block">New Campaign</a>
          </div>
        </motion.div>
      )}
    </motion.nav>
  );
};
