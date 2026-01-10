/**
 * Shared styles for ResearchDashboard
 */

export const dashboardStyles = `
  @keyframes float {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(20px, 20px); }
  }
  @keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
  }
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  @keyframes glow-green {
    0%, 100% { box-shadow: 0 0 20px rgba(34, 197, 94, 0.5), 0 2px 8px rgba(34, 197, 94, 0.3); }
    50% { box-shadow: 0 0 30px rgba(34, 197, 94, 0.8), 0 2px 12px rgba(34, 197, 94, 0.5); }
  }
  @keyframes glow-red {
    0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.5), 0 2px 8px rgba(239, 68, 68, 0.3); }
    50% { box-shadow: 0 0 30px rgba(239, 68, 68, 0.8), 0 2px 12px rgba(239, 68, 68, 0.5); }
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  .card-hover {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .card-hover:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  }
`;
