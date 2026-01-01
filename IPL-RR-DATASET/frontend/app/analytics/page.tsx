"use client";
import { useEffect, useState } from "react";
import { api } from "@/utils/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BarChart2, TrendingUp, Zap, Target } from "lucide-react";

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState("runs");
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData(activeTab);
  }, [activeTab]);

  const fetchData = async (category: string) => {
    setLoading(true);
    try {
      const res = await api.analytics.getLeaders(category);
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: "runs", label: "Top Run Getters", icon: TrendingUp },
    { id: "wickets", label: "Top Wicket Takers", icon: Target },
    { id: "mvp", label: "MVP Leaders", icon: BarChart2 },
    { id: "strike_rate", label: "Highest Strike Rates", icon: Zap },
  ];

  return (
    <div className="min-h-screen bg-black/90 p-8 text-white bg-[url('https://images.unsplash.com/photo-1531415074968-036ba1b575da?q=80&w=2607&auto=format&fit=crop')] bg-cover bg-fixed">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-md z-0 fixed" />
      
      <div className="relative z-10 max-w-6xl mx-auto space-y-8">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
            Deep Dive Analytics
            </h1>
            <div className="flex gap-2 flex-wrap justify-center">
            {tabs.map((tab) => (
                <Button
                key={tab.id}
                variant={activeTab === tab.id ? "neon" : "outline"}
                onClick={() => setActiveTab(tab.id)}
                className="gap-2"
                >
                <tab.icon className="w-4 h-4" />
                {tab.label}
                </Button>
            ))}
            </div>
        </div>

        <Card className="glass-panel border-white/10">
          <CardHeader>
            <CardTitle className="text-2xl text-cyan-400">
              {tabs.find(t => t.id === activeTab)?.label}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-64 flex items-center justify-center text-cyan-500 animate-pulse">
                Loading Data...
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-white/20 text-gray-400">
                      <th className="p-4">Rank</th>
                      {data.length > 0 && Object.keys(data[0]).map((key) => (
                        <th key={key} className="p-4 capitalize">{key.replace(/_/g, " ")}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.map((row, i) => (
                      <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="p-4 text-gray-500 font-mono">#{i + 1}</td>
                        {Object.values(row).map((val: any, j) => (
                          <td key={j} className="p-4 font-medium text-gray-200">
                            {typeof val === 'number' ? val.toLocaleString(undefined, { maximumFractionDigits: 2 }) : val}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
