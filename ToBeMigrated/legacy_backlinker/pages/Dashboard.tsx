
import { Navigation } from "@/components/navigation";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { KeywordResearch } from "@/components/dashboard/keyword-research";
import { ProspectAnalysis } from "@/components/dashboard/prospect-analysis";
import { EmailCampaigns } from "@/components/dashboard/email-campaigns";
import { CollaborationTracker } from "@/components/dashboard/collaboration-tracker";
import { AnalyticsSummary } from "@/components/dashboard/analytics-summary";

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gradient-bg">
      <Navigation />
      <div className="pt-16">
        <DashboardHeader />
        <div className="container mx-auto px-4 py-8 space-y-8">
          <AnalyticsSummary />
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            <KeywordResearch />
            <ProspectAnalysis />
          </div>
          <EmailCampaigns />
          <CollaborationTracker />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
