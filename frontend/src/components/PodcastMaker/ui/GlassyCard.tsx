import React from "react";
import { motion } from "framer-motion";
import { Paper, alpha } from "@mui/material";

export const GlassyCard = motion(Paper);

export const glassyCardSx = {
  borderRadius: 2,
  border: "1px solid rgba(0,0,0,0.08)",
  background: "#ffffff",
  p: 2.5,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

