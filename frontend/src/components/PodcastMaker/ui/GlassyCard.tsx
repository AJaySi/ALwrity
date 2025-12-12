import React from "react";
import { motion } from "framer-motion";
import { Paper, alpha } from "@mui/material";

export const GlassyCard = motion(Paper);

export const glassyCardSx = {
  borderRadius: 3,
  border: "1px solid rgba(15, 23, 42, 0.06)",
  background: "#ffffff",
  p: 3,
  boxShadow: "0 1px 3px rgba(15, 23, 42, 0.06), 0 4px 12px rgba(15, 23, 42, 0.04)",
  color: "#0f172a",
  transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
  "&:hover": {
    boxShadow: "0 4px 6px rgba(15, 23, 42, 0.08), 0 8px 24px rgba(15, 23, 42, 0.06)",
    borderColor: "rgba(15, 23, 42, 0.1)",
  },
};

