"use client";
import { useEffect, useState } from "react";
import { api } from "@/utils/api";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { BrainCircuit, Trophy, AlertCircle } from "lucide-react";

export default function PredictorPage() {
  const [activeMode, setActiveMode] = useState<"match" | "mvp">("match");
  const [metadata, setMetadata] = useState<any>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Form States
  const [matchForm, setMatchForm] = useState({ venue: "", toss_decision: "Batting", season: "2023" });
  const [mvpForm, setMvpForm] = useState({ 
      venue: "", season: "2023", batting_type: "Right Hand Bat", bowling_type: "Right-arm medium", batting_order: 3 
  });

  useEffect(() => {
    // Load metadata (Venues, etc)
    api.predictions.getMetadata().then(setMetadata).catch(console.error);
  }, []);

  const handlePredict = async () => {
    setError(null);
    setResult(null);
    try {
      if (activeMode === "match") {
        const res = await api.predictions.predictMatchWinner(matchForm);
        setResult(res);
      } else {
        const res = await api.predictions.predictMVP(mvpForm);
        setResult(res);
      }
    } catch (err) {
      setError("Prediction failed. Please check inputs.");
    }
  };

  return (
    <div className="min-h-screen p-8 bg-black/95 text-white bg-[url('https://images.unsplash.com/photo-1631194758628-71ec7c35137e?q=80&w=2532&auto=format&fit=crop')] bg-cover bg-center">
      <div className="absolute inset-0 bg-black/85 backdrop-blur-sm z-0 fixed" />
      
      <div className="relative z-10 max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-500">
            AI Predictor
          </h1>
          <p className="text-gray-400">Choose your model and forecast the future of the match.</p>
          
          <div className="flex justify-center gap-4 mt-6">
            <Button 
                variant={activeMode === "match" ? "neon" : "outline"} 
                onClick={() => { setActiveMode("match"); setResult(null); setError(null); }}
                className="w-40"
            >
                Match Winner
            </Button>
            <Button 
                variant={activeMode === "mvp" ? "neon" : "outline"} 
                onClick={() => { setActiveMode("mvp"); setResult(null); setError(null); }}
                className="w-40"
            >
                Player MVP
            </Button>
          </div>
        </div>

        <Card className="glass-panel border-green-500/20 max-w-2xl mx-auto">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <BrainCircuit className="w-6 h-6 text-green-400" />
                    {activeMode === "match" ? "Match Outcome Model" : "MVP Score Regressor"}
                </CardTitle>
                <CardDescription>
                    {activeMode === "match" 
                        ? "Predicts probability of Toss Winner winning the match based on Venue and Decision." 
                        : "Estimates a player's MVP impact score based on their role and match context."}
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Dynamic Form Fields */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <Label>Venue</Label>
                        <select 
                            className="w-full p-2 rounded-md bg-black/50 border border-white/20 text-white"
                            value={activeMode === "match" ? matchForm.venue : mvpForm.venue}
                            onChange={(e) => activeMode === "match" 
                                ? setMatchForm({...matchForm, venue: e.target.value}) 
                                : setMvpForm({...mvpForm, venue: e.target.value})}
                        >
                            <option value="">Select Venue</option>
                            {metadata?.venues?.map((v: string) => <option key={v} value={v}>{v}</option>)}
                        </select>
                    </div>
                    
                    <div className="space-y-2">
                        <Label>Season</Label>
                        <select 
                            className="w-full p-2 rounded-md bg-black/50 border border-white/20 text-white"
                            value={activeMode === "match" ? matchForm.season : mvpForm.season}
                            onChange={(e) => activeMode === "match" 
                                ? setMatchForm({...matchForm, season: e.target.value}) 
                                : setMvpForm({...mvpForm, season: e.target.value})}
                        >
                            {metadata?.seasons?.map((s: string) => <option key={s} value={s}>{s}</option>)}
                        </select>
                    </div>

                    {activeMode === "match" && (
                        <div className="space-y-2">
                            <Label>Toss Decision</Label>
                            <select 
                                className="w-full p-2 rounded-md bg-black/50 border border-white/20 text-white"
                                value={matchForm.toss_decision}
                                onChange={(e) => setMatchForm({...matchForm, toss_decision: e.target.value})}
                            >
                                <option value="Batting">Batting</option>
                                <option value="Fielding">Fielding</option>
                            </select>
                        </div>
                    )}

                    {activeMode === "mvp" && (
                        <>
                            <div className="space-y-2">
                                <Label>Batting Style</Label>
                                <select 
                                    className="w-full p-2 rounded-md bg-black/50 border border-white/20 text-white"
                                    value={mvpForm.batting_type}
                                    onChange={(e) => setMvpForm({...mvpForm, batting_type: e.target.value})}
                                >
                                    <option value="">Select Style</option>
                                    {metadata?.batting_styles?.map((s: string) => <option key={s} value={s}>{s}</option>)}
                                </select>
                            </div>
                            <div className="space-y-2">
                                <Label>Bowling Style</Label>
                                <select 
                                    className="w-full p-2 rounded-md bg-black/50 border border-white/20 text-white"
                                    value={mvpForm.bowling_type}
                                    onChange={(e) => setMvpForm({...mvpForm, bowling_type: e.target.value})}
                                >
                                    <option value="">Select Style</option>
                                    {metadata?.bowling_styles?.map((s: string) => <option key={s} value={s}>{s}</option>)}
                                </select>
                            </div>
                            <div className="space-y-2">
                                <Label>Batting Order</Label>
                                <Input 
                                    type="number"
                                    value={mvpForm.batting_order || ""}
                                    onChange={(e) => setMvpForm({...mvpForm, batting_order: e.target.value ? parseInt(e.target.value) : 0})}
                                    className="bg-black/50 border-white/20"
                                />
                            </div>
                        </>
                    )}
                </div>

                <Button className="w-full mt-4 bg-green-600 hover:bg-green-700 text-white" onClick={handlePredict}>
                    Run Prediction
                </Button>

                {/* Results Section */}
                {error && (
                    <div className="p-4 rounded-lg bg-red-900/50 border border-red-500/50 text-red-200 flex items-center gap-2">
                        <AlertCircle className="w-5 h-5" /> {error}
                    </div>
                )}

                {result && (
                    <div className="mt-6 p-6 rounded-xl bg-gradient-to-br from-green-900/40 to-blue-900/40 border border-green-500/30 animate-in fade-in zoom-in">
                        <h3 className="text-xl font-semibold mb-2 text-green-300">Analysis Result</h3>
                        {activeMode === "match" && result.win_probability !== undefined ? (
                            <div>
                                <p className="text-sm text-gray-400">Win Probability for Toss Winner:</p>
                                <div className="text-4xl font-bold text-white mt-1">
                                    {(result.win_probability * 100).toFixed(1)}%
                                </div>
                                <p className="text-xs text-green-400 mt-2">{result.message}</p>
                            </div>
                        ) : activeMode === "mvp" && result.predicted_mvp_score !== undefined ? (
                            <div>
                                <p className="text-sm text-gray-400">Projected MVP Score:</p>
                                <div className="text-4xl font-bold text-white mt-1">
                                    {result.predicted_mvp_score?.toFixed(1)}
                                </div>
                                <p className="text-xs text-blue-400 mt-2">Performance Level: {result.analysis}</p>
                            </div>
                        ) : (
                             <div className="text-gray-400">Loading results...</div>
                        )}
                    </div>
                )}
            </CardContent>
        </Card>
      </div>
    </div>
  );
}
