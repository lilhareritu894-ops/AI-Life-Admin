import React from "react";
import { motion } from "framer-motion";

export default function BentoCard({ children, className = "", delay = 0, glowColor = "cyan" }) {
  const glowStyles = {
    cyan: "hover:border-cyan-500/50 hover:shadow-cyan-500/10",
    emerald: "hover:border-emerald-500/50 hover:shadow-emerald-500/10",
    indigo: "hover:border-indigo-500/50 hover:shadow-indigo-500/10",
    amber: "hover:border-amber-500/50 hover:shadow-amber-500/10",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className={`bg-slate-900/70 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-5 shadow-2xl transition-all duration-300 ${
        glowStyles[glowColor] || glowStyles.cyan
      } ${className}`}
    >
      {children}
    </motion.div>
  );
}