const API_BASE_URL = "http://localhost:8000/api/v1";

export interface PlayerStats {
    player_name: string;
    [key: string]: any;
}

export const api = {
    analytics: {
        getLeaders: async (category: string, limit: number = 15) => {
            const res = await fetch(`${API_BASE_URL}/analytics/leaders/${category}?limit=${limit}`);
            if (!res.ok) throw new Error("Failed to fetch leaders");
            return res.json();
        },
    },
    predictions: {
        getMetadata: async () => {
            const res = await fetch(`${API_BASE_URL}/predict/metadata`);
            if (!res.ok) throw new Error("Failed to fetch metadata");
            return res.json();
        },
        predictMatchWinner: async (data: any) => {
            // Query params for FastAPI
            const params = new URLSearchParams({
                venue: data.venue,
                toss_decision: data.toss_decision,
                season: data.season
            });
            const res = await fetch(`${API_BASE_URL}/predict/match-winner?${params.toString()}`, {
                method: 'POST',
            });
            if (!res.ok) throw new Error("Prediction failed");
            return res.json();
        },
        predictMVP: async (data: any) => {
            const params = new URLSearchParams({
                venue: data.venue,
                season: data.season,
                batting_type: data.batting_type,
                bowling_type: data.bowling_type,
                batting_order: data.batting_order.toString()
            });
            const res = await fetch(`${API_BASE_URL}/predict/fantasy-mvp?${params.toString()}`, { method: 'POST' });
            if (!res.ok) throw new Error("Prediction failed");
            return res.json();
        }
    },
    players: {
        list: async (search: string = "", limit: number = 20) => {
            const res = await fetch(`${API_BASE_URL}/players/?search=${search}&limit=${limit}`);
            return res.json();
        },
        getSimilar: async (id: number) => {
            const res = await fetch(`${API_BASE_URL}/players/${id}/similar`);
            return res.json();
        }
    },
    venues: {
        getStats: async (venue: string) => {
            const res = await fetch(`${API_BASE_URL}/venues/${encodeURIComponent(venue)}`);
            if (!res.ok) throw new Error("Failed to fetch venue stats");
            return res.json();
        }
    },
    fantasy: {
        generateTeam: async (data: { team_a: string, team_b: string, venue: string, season: string }) => {
            const res = await fetch(`${API_BASE_URL}/fantasy/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });
            if (!res.ok) throw new Error("Failed to generate fantasy team");
            return res.json();
        }
    }
};
