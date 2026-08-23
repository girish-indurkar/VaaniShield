"use client";

import { RiskBand } from "@/lib/analysis";

const BAND_COLOR: Record<RiskBand, string> = {
  safe: "#2fd9a6",
  warning: "#f5a623",
  risk: "#ff4757",
};

const BAND_LABEL: Record<RiskBand, string> = {
  safe: "Likely Genuine",
  warning: "Caution Advised",
  risk: "High Impersonation Risk",
};

export default function RiskGauge({
  score,
  band,
}: {
  score: number;
  band: RiskBand;
}) {
  const radius = 84;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = BAND_COLOR[band];

  return (
    <div className="flex flex-col items-center">
      <div className="relative h-52 w-52">
        <svg viewBox="0 0 200 200" className="h-full w-full -rotate-90">
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke="#1f2530"
            strokeWidth="14"
          />
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{
              transition: "stroke-dashoffset 900ms cubic-bezier(.4,0,.2,1), stroke 500ms",
              filter: `drop-shadow(0 0 10px ${color}66)`,
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono text-5xl font-semibold" style={{ color }}>
            {score}
          </span>
          <span className="text-xs text-[#8b93a3] tracking-wide">/ 100 RISK</span>
        </div>
      </div>
      <div
        className="mt-4 rounded-full border px-4 py-1.5 text-sm font-medium"
        style={{ borderColor: `${color}55`, color, background: `${color}14` }}
      >
        {BAND_LABEL[band]}
      </div>
    </div>
  );
}
