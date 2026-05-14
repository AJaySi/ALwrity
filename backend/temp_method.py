    def _get_all_historical_usage(self, user_id: str) -> Dict[str, Any]:
        \ \\Get ALL historical usage data aggregated across all billing periods.\\\
        
        # Get all usage summaries for the user
        all_summaries = self.db.query(UsageSummary).filter(
            UsageSummary.user_id == user_id
        ).order_by(UsageSummary.billing_period.desc()).all()
        
        if not all_summaries:
            return {
                \billing_period\: \all\,
                \usage_status\: \active\,
                \total_calls\: 0,
                \total_tokens\: 0,
                \total_cost\: 0.0,
                \avg_response_time\: 0.0,
                \error_rate\: 0.0,
                \limits\: self.pricing_service.get_user_limits(user_id),
                \provider_breakdown\: {},
                \usage_percentages\: {},
                \historical_breakdown\: [],
                \last_updated\: datetime.now().isoformat()
            }
        
        # Aggregate all data
        total_calls = sum(s.total_calls or 0 for s in all_summaries)
        total_tokens = sum(s.total_tokens or 0 for s in all_summaries)
        total_cost = sum(float(s.total_cost or 0) for s in all_summaries)
        
        # Calculate weighted average response time
        total_weighted_time = sum((s.avg_response_time or 0) * (s.total_calls or 0) for s in all_summaries)
        avg_response_time = total_weighted_time / total_calls if total_calls > 0 else 0.0
        
        # Calculate overall error rate
        total_errors = sum((s.total_calls or 0) * (s.error_rate or 0) / 100 for s in all_summaries)
        error_rate = (total_errors / total_calls * 100) if total_calls > 0 else 0.0
        
        # Get user limits
        limits = self.pricing_service.get_user_limits(user_id)
        
        # Build historical breakdown
        historical_breakdown = []
        for s in all_summaries:
            try:
                status_val = s.usage_status.value
            except:
                status_val = str(s.usage_status)
            historical_breakdown.append({
                \billing_period\: s.billing_period,
                \total_calls\: s.total_calls or 0,
                \total_tokens\: s.total_tokens or 0,
                \total_cost\: float(s.total_cost or 0),
                \usage_status\: status_val,
                \updated_at\: s.updated_at.isoformat() if s.updated_at else None
            })
        
        # Determine overall status
        usage_status = \active\
        for s in all_summaries:
            try:
                status = s.usage_status.value
            except:
                status = str(s.usage_status)
            if status == \limit_reached\:
                usage_status = \limit_reached\
                break
            elif status == \warning\ and usage_status != \limit_reached\:
                usage_status = \warning\
        
        return {
            \billing_period\: \all\,
            \usage_status\: usage_status,
            \total_calls\: total_calls,
            \total_tokens\: total_tokens,
            \total_cost\: round(total_cost, 2),
            \avg_response_time\: round(avg_response_time, 2),
            \error_rate\: round(error_rate, 2),
            \limits\: limits,
            \provider_breakdown\: {},
            \usage_percentages\: {},
            \historical_breakdown\: historical_breakdown,
            \last_updated\: datetime.now().isoformat()
        }
