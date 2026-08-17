"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { VolumeDataPoint } from "@/services/sorobanApi";
import { useState } from "react";

interface VolumeChartProps {
  data: VolumeDataPoint[];
}

const COLORS = {
  soroswap: "#6366f1",
  phoenix: "#f59e0b",
  blend: "#10b981",
};

const formatUSD = (value: number) => {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value}`;
};

const formatDate = (dateStr: string) => {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
};

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-slate-800 border border-slate-600 rounded-xl p-3 shadow-xl text-sm min-w-[160px]">
      <p className="text-slate-400 font-medium mb-2">
        {label ? formatDate(label) : ""}
      </p>
      {payload.map((entry) => (
        <div key={entry.name} className="flex justify-between items-center gap-4 mb-1">
          <span className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full inline-block"
              style={{ background: entry.color }}
            />
            <span className="text-slate-300 capitalize">{entry.name}</span>
          </span>
          <span className="font-semibold text-slate-100">
            {formatUSD(entry.value)}
          </span>
        </div>
      ))}
    </div>
  );
};

// Convert data to CSV string
const convertToCSV = (data: VolumeDataPoint[]): string => {
  if (!data.length) return "";
  
  const headers = ["Date", "Soroswap TVL (USD)", "Phoenix TVL (USD)", "Blend TVL (USD)", "Total TVL (USD)"];
  const rows = data.map((point) => [
    point.date,
    point.soroswap.toString(),
    point.phoenix.toString(),
    point.blend.toString(),
    point.total.toString(),
  ]);
  
  return [headers.join(","), ...rows.map((row) => row.join(","))].join("\n");
};

// Trigger CSV download
const downloadCSV = (csv: string, filename: string) => {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export default function VolumeChart({ data }: VolumeChartProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = () => {
    setIsExporting(true);
    const csv = convertToCSV(data);
    const filename = `soroban-defi-tvl-${new Date().toISOString().split("T")[0]}.csv`;
    downloadCSV(csv, filename);
    setIsExporting(false);
  };

  return (
    <div className="card w-full min-w-0 overflow-hidden">
      <div className="card-header flex items-center justify-between">
        <h3 className="card-title">Historical TVL Trend (30 Days)</h3>
        <button
          onClick={handleExport}
          disabled={isExporting || !data.length}
          className="btn btn-sm btn-ghost text-slate-300 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          aria-label="Export TVL data as CSV"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          {isExporting ? "Exporting..." : "Export CSV"}
        </button>
      </div>
      <div className="card-body p-4">
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              {Object.entries(COLORS).map(([key, color]) => (
                <linearGradient key={key} id={`color-${key}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickFormatter={formatDate}
              axisLine={false}
              tickLine={false}
              dy={10}
            />
            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickFormatter={formatUSD}
              axisLine={false}
              tickLine={false}
              width={60}
              dx={-10}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: 10 }}
              formatter={(name) => name.charAt(0).toUpperCase() + name.slice(1)}
            />
            {Object.entries(COLORS).map(([key, color]) => (
              <Area
                key={key}
                type="monotone"
                dataKey={key}
                stroke={color}
                fillOpacity={1}
                fill={`url(#color-${key})`}
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
        
        {/* Empty state */}
        {!data.length && (
          <div className="flex items-center justify-center h-64 text-slate-500">
            <p>No historical data available</p>
          </div>
        )}
      </div>
    </div>
  );
}