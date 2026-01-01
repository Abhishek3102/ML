"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Sparkles, Trophy, Users } from "lucide-react";
import { api } from "@/utils/api";
import { cn } from "@/utils/cn";

export default function FantasyPage() {
  const [form, setForm] = useState({ 
    team_a: "Chennai Super Kings", 
    team_b: "Mumbai Indians", 
    venue: "Wankhede Stadium",
    season: "2023"
  });
  const [loading, setLoading] = useState(false);
  const [dreamTeam, setDreamTeam] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
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

      <div className="relative z-10 max-w-6xl mx-auto space-y-8 pt-20">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
            Fantasy Optimizer
          </h1>
          <p className="text-gray-300 text-xl">Build the ultimate dream team using AI-driven MVP predictions.</p>
        </div>

        {/* Input Form */}
        <Card className="glass-panel border-purple-500/20 max-w-2xl mx-auto">
            <CardContent className="p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <Label>Team A</Label>
                        <Input 
                            value={form.team_a} 
                            onChange={(e) => setForm({...form, team_a: e.target.value})}
                            className="bg-black/50 border-white/20 text-white"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label>Team B</Label>
                        <Input 
                            value={form.team_b} 
                            onChange={(e) => setForm({...form, team_b: e.target.value})}
                            className="bg-black/50 border-white/20 text-white"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label>Venue</Label>
                        <Input 
                            value={form.venue} 
                            onChange={(e) => setForm({...form, venue: e.target.value})}
                            className="bg-black/50 border-white/20 text-white"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label>Season</Label>
                        <Input 
                            value={form.season} 
                            onChange={(e) => setForm({...form, season: e.target.value})}
                            className="bg-black/50 border-white/20 text-white"
                        />
                    </div>
                </div>
                
                <Button 
                    onClick={handleGenerate} 
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3"
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
                            "glass-panel border-white/10 hover:bg-white/10 transition-colors",
                            idx < 3 ? "border-yellow-500/50 shadow-[0_0_15px_rgba(234,179,8,0.2)]" : ""
                        )}>
                            <CardContent className="p-4 flex items-center gap-4">
                                <div className={cn(
                                    "w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg",
                                    idx === 0 ? "bg-yellow-500 text-black" : 
                                    idx === 1 ? "bg-gray-300 text-black" :
                                    idx === 2 ? "bg-amber-700 text-white" : "bg-white/10 text-white"
                                )}>
                                    {idx + 1}
                                </div>
                                <div>
                                    <h3 className="font-semibold text-white">{player.player}</h3>
                                    <p className="text-xs text-gray-400">{player.team} • {player.role}</p>
                                </div>
                                <div className="ml-auto text-right">
                                    <span className="block text-xl font-bold text-cyan-400">{player.predicted_points.toFixed(1)}</span>
                                    <span className="text-[10px] uppercase tracking-wider text-gray-500">MVP Pts</span>
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
