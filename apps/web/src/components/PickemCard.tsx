"use client";

import type { PickemGame } from "@/lib/api";

interface PickemCardProps {
  game: PickemGame;
  pickedTeamId: number | null;
  onPick: (gameId: number, teamId: number) => void;
  locked: boolean;
  result?: { is_correct: boolean | null };
}

export default function PickemCard({ game, pickedTeamId, onPick, locked, result }: PickemCardProps) {
  const isFinal = game.status === "final";

  function teamButton(teamId: number, teamName: string | null, score: number | null, isHome: boolean) {
    const selected = pickedTeamId === teamId;
    const correct = result?.is_correct === true && selected;
    const wrong = result?.is_correct === false && selected;

    return (
      <button
        onClick={() => !locked && onPick(game.game_id, teamId)}
        disabled={locked}
        className={`flex-1 rounded-lg p-3 text-center transition-all border ${
          correct ? "border-green-500 bg-green-500/10" :
          wrong ? "border-red-500 bg-red-500/10" :
          selected ? "border-crimson bg-crimson/10" :
          "border-steel-gray/30 hover:border-steel-gray"
        } ${locked && !selected ? "opacity-50" : ""}`}
      >
        <div className="text-xs text-steel-gray mb-1">{isHome ? "HOME" : "AWAY"}</div>
        <div className={`font-semibold text-sm ${selected ? "text-white" : "text-steel-gray"}`}>
          {teamName || `Team #${teamId}`}
        </div>
        {isFinal && score !== null && (
          <div className="text-lg font-bold mt-1">{score}</div>
        )}
      </button>
    );
  }

  return (
    <div className="rounded-lg border border-steel-gray/30 p-4 bg-charcoal">
      {game.game_date && (
        <div className="text-xs text-steel-gray mb-2">
          {new Date(game.game_date + "T00:00:00").toLocaleDateString("en-US", {
            weekday: "short", month: "short", day: "numeric",
          })}
          {isFinal && <span className="ml-2">FINAL</span>}
        </div>
      )}
      <div className="flex gap-3">
        {teamButton(game.home_team_id, game.home_team_name, game.home_score, true)}
        <div className="flex items-center text-steel-gray text-sm font-bold">VS</div>
        {teamButton(game.away_team_id, game.away_team_name, game.away_score, false)}
      </div>
      {result && result.is_correct !== null && (
        <div className={`mt-2 text-xs text-center font-bold ${result.is_correct ? "text-green-500" : "text-red-500"}`}>
          {result.is_correct ? "CORRECT" : "WRONG"}
        </div>
      )}
    </div>
  );
}
