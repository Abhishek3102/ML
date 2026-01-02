"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Sparkles, Trophy, Users, Flag, Calendar, Activity } from "lucide-react";
import { api } from "@/utils/api";
import { cn } from "@/utils/cn";

const countryFlags: Record<string, string> = {
    "India": "🇮🇳", "Australia": "🇦🇺", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "South Africa": "🇿🇦",
    "New Zealand": "🇳🇿", "West Indies": "🌴", "Pakistan": "🇵🇰", "Sri Lanka": "🇱🇰",
    "Afghanistan": "🇦🇫", "Bangladesh": "🇧🇩", "Ireland": "🇮🇪", "Zimbabwe": "🇿🇼",
    "Unknown": "🏳️"
};

const getFlag = (nation: string) => countryFlags[nation] || "🏳️";

export default function FantasyPage() {
  const [form, setForm] = useState({ 
    team_a: "", 
    team_b: "", 
    venue: "",
    season: "2024"
  });
  const [meta, setMeta] = useState<{ teams: string[], venues: string[], seasons: string[] }>({ teams: [], venues: [], seasons: [] });
  const [loading, setLoading] = useState(false);
  const [dreamTeam, setDreamTeam] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.predictions.getMetadata().then((data: any) => {
        setMeta({ 
            teams: data.teams || [], 
            venues: data.venues || [],
            seasons: data.seasons || [] 
        });
    });
  }, []);

  const handleGenerate = async () => {
    if (!form.team_a || !form.team_b || !form.venue || !form.season) {
        setError("Please select all fields.");
        return;
    }
    setLoading(true);
    setError(null);
    try {
        const res = await api.fantasy.generateTeam(form);
        setDreamTeam(res.dream_team);
    } catch (err) {
        setError("Failed to generate team. Ensure team names match the roster.");
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-[url('https://images.unsplash.com/photo-1531415074968-055db64351a6?q=80&w=2544&auto=format&fit=crop')] bg-cover bg-center bg-fixed">
       <div className="absolute inset-0 bg-black/70 z-0 fixed" />

      <div className="relative z-10 max-w-7xl mx-auto space-y-8 pt-20">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
            Fantasy Optimizer
          </h1>
          <p className="text-gray-300 text-xl">Build the ultimate dream team using AI-driven MVP predictions.</p>
        </div>

        {/* Input Form */}
        <Card className="glass-panel border-purple-500/20 max-w-3xl mx-auto">
            <CardContent className="p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label>Team A</Label>
                        <select 
                            className="w-full p-3 rounded-md bg-black/50 border border-white/20 text-white focus:ring-2 focus:ring-purple-500 outline-none"
                            value={form.team_a}
                            onChange={(e) => setForm({...form, team_a: e.target.value})}
                        >
                            <option value="">Select Team</option>
                            {meta.teams.filter(t => t !== form.team_b).map(t => (
                                <option key={t} value={t}>{t}</option>
                            ))}
                        </select>
                    </div>
                    <div className="space-y-2">
                        <Label>Team B</Label>
                        <select 
                            className="w-full p-3 rounded-md bg-black/50 border border-white/20 text-white focus:ring-2 focus:ring-purple-500 outline-none"
                            value={form.team_b}
                            onChange={(e) => setForm({...form, team_b: e.target.value})}
                        >
                            <option value="">Select Team</option>
                            {meta.teams.filter(t => t !== form.team_a).map(t => (
                                <option key={t} value={t}>{t}</option>
                            ))}
                        </select>
                    </div>
                    <div className="space-y-2">
                        <Label>Venue</Label>
                        <select 
                            className="w-full p-3 rounded-md bg-black/50 border border-white/20 text-white focus:ring-2 focus:ring-purple-500 outline-none"
                            value={form.venue}
                            onChange={(e) => setForm({...form, venue: e.target.value})}
                        >
                            <option value="">Select Venue</option>
                            {meta.venues.map(v => (
                                <option key={v} value={v}>{v}</option>
                            ))}
                        </select>
                    </div>
                    <div className="space-y-2">
                        <Label>Season</Label>
                        <select 
                            className="w-full p-3 rounded-md bg-black/50 border border-white/20 text-white focus:ring-2 focus:ring-purple-500 outline-none"
                            value={form.season}
                            onChange={(e) => setForm({...form, season: e.target.value})}
                        >
                            <option value="">Select Season</option>
                            {meta.seasons.map(s => (
                                <option key={s} value={s}>{s}</option>
                            ))}
                        </select>
                    </div>
                </div>
                
                <Button 
                    onClick={handleGenerate} 
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 text-lg rounded-xl transition-all hover:scale-[1.02]"
                >
                    {loading ? "Simulating Match..." : "Generate Dream 11"}
                </Button>
                
                {error && <p className="text-red-400 text-center">{error}</p>}
            </CardContent>
        </Card>

        {/* Results Grid */}
        {dreamTeam && (
            <div className="animate-in fade-in slide-in-from-bottom-8 duration-700 space-y-6">
                <div className="flex items-center justify-center gap-2 text-2xl font-bold text-white">
                    <Trophy className="text-yellow-400 w-8 h-8" />
                    <span>Projected Best XI</span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {dreamTeam.map((player, idx) => (
                        <Card key={idx} className={cn(
                            "glass-panel border-white/10 hover:bg-white/10 transition-colors group relative overflow-hidden",
                            idx < 3 ? "border-yellow-500/50 shadow-[0_0_20px_rgba(234,179,8,0.15)]" : ""
                        )}>
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <span className="text-6xl">{getFlag(player.nationality)}</span>
                            </div>
                            
                            <CardContent className="p-5 flex gap-4">
                                <div className={cn(
                                    "w-12 h-12 rounded-full flex shrink-0 items-center justify-center font-bold text-lg shadow-lg",
                                    idx === 0 ? "bg-gradient-to-br from-yellow-400 to-yellow-600 text-black" : 
                                    idx === 1 ? "bg-gradient-to-br from-gray-300 to-gray-500 text-black" :
                                    idx === 2 ? "bg-gradient-to-br from-amber-700 to-amber-900 text-white" : "bg-white/10 text-white"
                                )}>
                                    {idx + 1}
                                </div>
                                <div className="flex-1 space-y-2">
                                    <div>
                                        <div className="flex items-center justify-between">
                                            <h3 className="font-bold text-white text-lg leading-tight truncate pr-2">{player.player}</h3>
                                            <span className="text-2xl" title={player.nationality}>{getFlag(player.nationality)}</span>
                                        </div>
                                        <p className="text-xs text-purple-300 font-medium uppercase tracking-wider">{player.team}</p>
                                    </div>
                                    
                                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-400 mt-2 bg-black/20 p-2 rounded-lg">
                                        <div className="flex items-center gap-1">
                                            <Activity className="w-3 h-3 text-cyan-400" />
                                            <span>{player.role} ({player.batting_hand})</span>
                                        </div>
                                        {player.bowling_style !== 'None' && (
                                            <div className="flex items-center gap-1">
                                                <Sparkles className="w-3 h-3 text-pink-400" />
                                                <span>{player.bowling_style}</span>
                                            </div>
                                        )}
                                        <div className="flex items-center gap-1">
                                            <Calendar className="w-3 h-3 text-yellow-400" />
                                            <span>{player.age} Yrs</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex flex-col justify-center items-end border-l border-white/10 pl-4">
                                    <span className="block text-2xl font-black text-cyan-400">{player.predicted_points.toFixed(0)}</span>
                                    <span className="text-[10px] font-bold text-gray-500">MVP PTS</span>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        )}
      </div>
    </div>
  );
}
