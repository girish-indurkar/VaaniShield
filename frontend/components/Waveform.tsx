"use client";

import { Chunk, bandFor } from "@/lib/analysis";

const BAND_COLOR = {
  safe: "#2fd9a6",
  warning: "#f5a623",
  risk: "#ff4757",
};

export default function Waveform({
  chunks,
  active,
  onSelect,
  selected,
}: {
  chunks: Chunk[];
  active: boolean;
  onSelect: (idx: number) => void;
  selected: number | null;
}) {
  return (
    <div className="flex h-28 items-end gap-1.5 rounded-xl border border-[#1f2530] bg-[#0d0f15] p-4">
      {chunks.map((c, i) => {
        const color = BAND_COLOR[bandFor(c.score)];
        const heightPct = Math.max(12, c.score);
        return (
          <button
            key={i}
            onClick={() => onSelect(i)}
            className="group relative flex-1 h-full flex items-end"
            title={`${c.startSec}s–${c.endSec}s · ${c.score}% synthetic-likelihood`}
          >
            <div
              className={`w-full rounded-sm origin-bottom transition-[height] duration-500 ${
                active ? "animate-pulse-bar" : ""
              } ${selected === i ? "ring-2 ring-white/70" : ""}`}
              style={{
                height: `${heightPct}%`,
                background: `linear-gradient(180deg, ${color}, ${color}55)`,
                animationDelay: `${i * 90}ms`,
              }}
            />
          </button>
        );
      })}
    </div>
  );
}
