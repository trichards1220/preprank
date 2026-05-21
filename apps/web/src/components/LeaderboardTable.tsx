import type { LeaderboardRow, SchoolLeaderboardRow } from "@/lib/api";

interface IndividualProps { type: "individual"; rows: LeaderboardRow[]; }
interface SchoolProps { type: "school"; rows: SchoolLeaderboardRow[]; }
type LeaderboardTableProps = IndividualProps | SchoolProps;

export default function LeaderboardTable(props: LeaderboardTableProps) {
  if (props.type === "individual") {
    return (
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-steel-gray text-steel-gray uppercase tracking-wide text-xs">
              <th className="px-3 py-2 w-12">#</th>
              <th className="px-3 py-2">Name</th>
              <th className="px-3 py-2 text-center">Correct</th>
              <th className="px-3 py-2 text-center">Total</th>
              <th className="px-3 py-2 text-center">Accuracy</th>
              <th className="px-3 py-2 text-right">Points</th>
            </tr>
          </thead>
          <tbody>
            {props.rows.map((r) => (
              <tr key={r.user_id} className="border-b border-steel-gray/20 hover:bg-charcoal/50">
                <td className={`px-3 py-2 font-bold ${r.rank <= 3 ? "text-crimson" : "text-steel-gray"}`}>{r.rank}</td>
                <td className="px-3 py-2 font-semibold">{r.display_name}</td>
                <td className="px-3 py-2 text-center">{r.total_correct}</td>
                <td className="px-3 py-2 text-center text-steel-gray">{r.total_picks}</td>
                <td className="px-3 py-2 text-center">{r.accuracy_pct}%</td>
                <td className="px-3 py-2 text-right font-mono font-bold">{r.total_points}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {props.rows.length === 0 && <p className="mt-4 text-center text-steel-gray text-sm">No entries yet.</p>}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-steel-gray text-steel-gray uppercase tracking-wide text-xs">
            <th className="px-3 py-2 w-12">#</th>
            <th className="px-3 py-2">School</th>
            <th className="px-3 py-2 text-center">Correct</th>
            <th className="px-3 py-2 text-center">Total</th>
            <th className="px-3 py-2 text-center">Accuracy</th>
            <th className="px-3 py-2 text-right">Participants</th>
          </tr>
        </thead>
        <tbody>
          {props.rows.map((r) => (
            <tr key={r.school_id} className="border-b border-steel-gray/20 hover:bg-charcoal/50">
              <td className={`px-3 py-2 font-bold ${r.rank <= 3 ? "text-crimson" : "text-steel-gray"}`}>{r.rank}</td>
              <td className="px-3 py-2 font-semibold">{r.school_name}</td>
              <td className="px-3 py-2 text-center">{r.total_correct}</td>
              <td className="px-3 py-2 text-center text-steel-gray">{r.total_picks}</td>
              <td className="px-3 py-2 text-center">{r.accuracy_pct}%</td>
              <td className="px-3 py-2 text-right">{r.participant_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {props.rows.length === 0 && <p className="mt-4 text-center text-steel-gray text-sm">No school data yet. Follow a team to represent your school!</p>}
    </div>
  );
}
