
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  TrendingUp, 
  Mail, 
  Users, 
  CheckCircle,
  Globe,
  Eye,
  MessageSquare,
  Target
} from "lucide-react";

export const AnalyticsSummary = () => {
  const stats = [
    {
      title: "Total Prospects",
      value: "1,247",
      change: "+12.5%",
      icon: Users,
      color: "text-primary"
    },
    {
      title: "Emails Sent",
      value: "856",
      change: "+8.3%",
      icon: Mail,
      color: "text-secondary"
    },
    {
      title: "Response Rate",
      value: "24.8%",
      change: "+3.2%",
      icon: MessageSquare,
      color: "text-accent"
    },
    {
      title: "Backlinks Secured",
      value: "187",
      change: "+15.7%",
      icon: CheckCircle,
      color: "text-primary"
    },
    {
      title: "Domain Authority Avg",
      value: "68.5",
      change: "+2.1%",
      icon: Globe,
      color: "text-secondary"
    },
    {
      title: "Open Rate",
      value: "42.3%",
      change: "+5.4%",
      icon: Eye,
      color: "text-accent"
    },
    {
      title: "Active Campaigns",
      value: "12",
      change: "+2",
      icon: Target,
      color: "text-primary"
    },
    {
      title: "Conversion Rate",
      value: "18.6%",
      change: "+4.1%",
      icon: TrendingUp,
      color: "text-secondary"
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <Card className="neural-glow">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            Campaign Analytics Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                className="p-4 rounded-lg glass-card border hover:scale-105 transition-transform duration-300"
                whileHover={{ scale: 1.05 }}
              >
                <div className="flex flex-col items-center text-center">
                  <stat.icon className={`w-6 h-6 mb-2 ${stat.color}`} />
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <div className="text-xs text-muted-foreground mb-1">{stat.title}</div>
                  <div className="text-xs text-green-500 font-medium">{stat.change}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};
