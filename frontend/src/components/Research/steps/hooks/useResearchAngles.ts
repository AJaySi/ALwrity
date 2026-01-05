/**
 * Hook for generating research angles with persona support
 */

import { useState, useEffect } from 'react';
import { generateResearchAngles } from '../../../../utils/researchAngles';

interface ResearchPersona {
  research_angles?: string[];
}

export const useResearchAngles = (
  keywords: string[],
  industry: string,
  researchPersona: ResearchPersona | null
): string[] => {
  const [researchAngles, setResearchAngles] = useState<string[]>([]);

  useEffect(() => {
    if (keywords.length > 0) {
      const query = keywords.join(' ');
      let angles: string[] = [];
      
      // Priority 1: Use research persona angles if available and relevant
      if (researchPersona?.research_angles && researchPersona.research_angles.length > 0) {
        // Filter persona angles that are relevant to the current query
        const relevantPersonaAngles = researchPersona.research_angles
          .filter(angle => {
            const angleLower = angle.toLowerCase();
            const queryLower = query.toLowerCase();
            // Check if angle contains any keyword from query or vice versa
            return keywords.some(kw => angleLower.includes(kw.toLowerCase()) || queryLower.includes(kw.toLowerCase())) ||
                   angleLower.includes(queryLower) || queryLower.includes(angleLower);
          })
          .slice(0, 3); // Use top 3 relevant persona angles
        
        angles.push(...relevantPersonaAngles);
      }
      
      // Priority 2: Generate additional angles using pattern matching
      const generatedAngles = generateResearchAngles(query, industry);
      
      // Merge and deduplicate, prioritizing persona angles
      const allAngles = [...angles, ...generatedAngles];
      const uniqueAngles = Array.from(new Set(allAngles.map(a => a.toLowerCase())))
        .slice(0, 5) // Limit to 5 total
        .map(a => {
          // Find original casing from persona angles first, then generated
          const personaMatch = angles.find(pa => pa.toLowerCase() === a);
          if (personaMatch) return personaMatch;
          const generatedMatch = generatedAngles.find(ga => ga.toLowerCase() === a);
          return generatedMatch || a.charAt(0).toUpperCase() + a.slice(1);
        });
      
      setResearchAngles(uniqueAngles);
    } else {
      setResearchAngles([]);
    }
  }, [keywords, industry, researchPersona]);

  return researchAngles;
};
