"use client";
import { useEffect, useState } from "react";
import { api } from "@/utils/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Users, Search, Star, Hexagon } from "lucide-react";

export default function PlayersPage() {
  const [players, setPlayers] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [selectedPlayer, setSelectedPlayer] = useState<any>(null);
  const [similarPlayers, setSimilarPlayers] = useState<any[]>([]);

  useEffect(() => {
    // Initial load
    loadPlayers();
  }, []);

  const loadPlayers = async (q = "") => {
    try {
      const res = await api.players.list(q, 50);
      setPlayers(res);
    } catch (e) { console.error(e); }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadPlayers(search);
  };

  const handleSelectPlayer = async (player: any) => {
    setSelectedPlayer(player);
    try {
      const sim = await api.players.getSimilar(player.player_id);
      setSimilarPlayers(sim);
    } catch (e) { console.error(e); }
  };

  const getClusterColor = (label: number) => {
    const colors = ["bg-red-500", "bg-blue-500", "bg-green-500", "bg-purple-500", "bg-yellow-500"];
    return colors[label % colors.length];
  };

  return (
    <div className="min-h-screen bg-black/95 text-white p-8 bg-[url('https://images.unsplash.com/photo-1593341646261-23d906152a42?q=80&w=2670&auto=format&fit=crop')] bg-cover bg-fixed">
      <div className="absolute inset-0 bg-black/90 backdrop-blur-md z-0 fixed" />
      
      <div className="relative z-10 max-w-7xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold text-center bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-500">
            Player Intelligence
        </h1>

        {/* Search */}
        <div className="max-w-md mx-auto flex gap-2">
            <Input 
                placeholder="Search Player Name..." 
                className="bg-black/50 border-white/20 text-white"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
            />
            <Button onClick={handleSearch} variant="secondary">
                <Search className="w-4 h-4" />
            </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Player List */}
            <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4 h-[800px] overflow-y-auto pr-2 custom-scrollbar">
                {players.map((p) => (
                    <Card 
                        key={p.player_id} 
                        className={`cursor-pointer hover:border-purple-500/50 transition-all ${selectedPlayer?.player_id === p.player_id ? 'border-purple-500 bg-purple-900/20' : 'border-white/10'}`}
                        onClick={() => handleSelectPlayer(p)}
                    >
                        <CardHeader className="flex flex-row justify-between items-start pb-2">
                            <div>
                                <CardTitle className="text-lg">{p.player_name}</CardTitle>
                                <div className="text-xs text-gray-400 mt-1">MVP Score: {p.total_mvp?.toFixed(0)}</div>
                            </div>
                            <div className={`px-2 py-1 rounded text-xs font-bold text-white ${getClusterColor(p.cluster_label)}`}>
                                Cluster {p.cluster_label}
                            </div>
                        </CardHeader>
                        <CardContent>
                             <div className="text-xs text-gray-400 grid grid-cols-2 gap-2">
                                <div>Avg: <span className="text-white">{p.batting_avg?.toFixed(1)}</span></div>
                                <div>SR: <span className="text-white">{p.true_strike_rate?.toFixed(1)}</span></div>
                             </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Sidebar Details */}
            <div className="lg:col-span-1">
                {selectedPlayer ? (
                    <div className="sticky top-8 space-y-6 animate-in slide-in-from-right">
                        <Card className="border-purple-500/50 bg-black/60 shadow-2xl shadow-purple-900/20">
                            <CardHeader>
                                <CardTitle className="text-2xl text-purple-300">{selectedPlayer.player_name}</CardTitle>
                                <div className="flex items-center gap-2 text-sm text-gray-300">
                                    <Hexagon className="w-4 h-4 text-purple-500" /> 
                                    Cluster Type: <span className="font-bold text-white">{selectedPlayer.cluster_label}</span>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="p-4 rounded bg-white/5 border border-white/10">
                                    <div className="text-3xl font-bold text-center text-green-400">{selectedPlayer.total_mvp?.toFixed(0)}</div>
                                    <div className="text-center text-xs text-gray-500 uppercase tracking-widest">Total Impact Score</div>
                                </div>
                            </CardContent>
                        </Card>
                        
                        <div className="space-y-2">
                            <h3 className="text-lg font-semibold text-gray-300 flex items-center gap-2">
                                <Users className="w-5 h-5" /> Similar Players
                            </h3>
                            {similarPlayers.map((sim) => (
                                <div key={sim.player_name} className="p-3 rounded bg-white/5 border border-white/5 flex justify-between items-center">
                                    <span className="text-sm">{sim.player_name}</span>
                                    <span className="text-xs text-gray-400">MVP: {sim.total_mvp?.toFixed(0)}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500 border border-dashed border-white/10 rounded-xl p-8">
                        <Star className="w-12 h-12 mb-4 opacity-20" />
                        <p>Select a player to view details and find similar profiles.</p>
                    </div>
                )}
            </div>
        </div>
      </div>
    </div>
  );
}
