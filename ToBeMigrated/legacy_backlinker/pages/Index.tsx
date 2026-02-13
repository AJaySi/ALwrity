import { Navigation } from "@/components/navigation";
import { HeroSection } from "@/components/hero-section";
import { FeaturesSection } from "@/components/features-section";
import { DashboardPreview } from "@/components/dashboard-preview";
import { ComparisonSection } from "@/components/comparison-section";
import { PricingSection } from "@/components/pricing-section";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Navigation />
      <HeroSection />
      <FeaturesSection />
      <DashboardPreview />
      <ComparisonSection />
      <PricingSection />
    </div>
  );
};

export default Index;
