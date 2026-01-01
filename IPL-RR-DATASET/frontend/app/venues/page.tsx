"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { MapPin, TrendingUp, Target, Activity } from "lucide-react";
import { api } from "@/utils/api";

export default function VenuesPage() {
  const [venueName, setVenueName] = useState("Wankhede Stadium");
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
        const data = await api.venues.getStats(venueName);
        setStats(data);
    } catch (err) {
        setError("Venue not found. Try 'Eden Gardens' or 'M Chinnaswamy Stadium'.");
        setStats(null);
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-[url('https://images.unsplash.com/photo-1587560699334-cc4da63c24b9?q=80&w=2669&auto=format&fit=crop')] bg-cover bg-center bg-fixed">
       <div className="absolute inset-0 bg-black/60 z-0 fixed" />

      <div className="relative z-10 max-w-6xl mx-auto space-y-8 pt-20">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">
            Venue Analysis
          </h1>
          <p className="text-gray-300 text-xl">Deep dive into stadium stats and pitch reports.</p>
        </div>

        {/* Search Bar */}
        <div className="max-w-xl mx-auto flex gap-4">
            <Input 
                value={venueName}
                onChange={(e) => setVenueName(e.target.value)}
                placeholder="Enter Stadium Name..."
                className="bg-black/50 border-white/20 text-white h-12"
            />
            <Button onClick={handleSearch} disabled={loading} className="h-12 px-8 bg-cyan-600 hover:bg-cyan-700">
                {loading ? "Analyzing..." : "Analyze"}
            </Button>
        </div>
        {error && <p className="text-center text-red-400">{error}</p>}

        {/* Stats Grid */}
        {stats && (
             <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
                <StatCard 
                    title="Bat Initial Win %" 
                    value={`${stats.bat_first_win_pct}%`} 
                    desc="Wins when batting first"
                    icon={<Target className="text-cyan-400" />}
                />
                <StatCard 
                    title="Chasing Win %" 
                    value={`${stats.chasing_win_pct}%`} 
                    desc="Wins when chasing"
                    icon={<TrendingUp className="text-green-400" />}
                />
                <StatCard 
                    title="Toss Impact" 
                    value={`${stats.toss_win_impact}%`} 
                    desc="Win prob if toss won"
                    icon={<Activity className="text-purple-400" />}
                />
                <StatCard 
                    title="Avg Score" 
                    value={stats.avg_score_estimate} 
                    desc="Estimated 1st Innings"
                    icon={<MapPin className="text-yellow-400" />}
                />
             </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value, desc, icon }: any) {
    return (
        <Card className="glass-panel border-cyan-500/20">
            <CardContent className="p-6 flex flex-col items-center text-center gap-4">
                <div className="p-3 bg-white/10 rounded-full">{icon}</div>
                <div>
                    <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
                    <div className="text-3xl font-bold text-white mt-1">{value}</div>
                    <p className="text-xs text-gray-500 mt-2">{desc}</p>
                </div>
            </CardContent>
        </Card>
    );
}
