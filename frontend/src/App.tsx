import { useState } from 'react'
import './App.css'

interface NFLTeam {
  name: string;
  abbreviation: string;
  conference: 'AFC' | 'NFC';
  division: 'North' | 'South' | 'East' | 'West';
}

const NFL_TEAMS: NFLTeam[] = [
  // AFC North
  { name: 'Baltimore Ravens', abbreviation: 'BAL', conference: 'AFC', division: 'North' },
  { name: 'Cincinnati Bengals', abbreviation: 'CIN', conference: 'AFC', division: 'North' },
  { name: 'Cleveland Browns', abbreviation: 'CLE', conference: 'AFC', division: 'North' },
  { name: 'Pittsburgh Steelers', abbreviation: 'PIT', conference: 'AFC', division: 'North' },
  // AFC South
  { name: 'Houston Texans', abbreviation: 'HOU', conference: 'AFC', division: 'South' },
  { name: 'Indianapolis Colts', abbreviation: 'IND', conference: 'AFC', division: 'South' },
  { name: 'Jacksonville Jaguars', abbreviation: 'JAX', conference: 'AFC', division: 'South' },
  { name: 'Tennessee Titans', abbreviation: 'TEN', conference: 'AFC', division: 'South' },
  // AFC East
  { name: 'Buffalo Bills', abbreviation: 'BUF', conference: 'AFC', division: 'East' },
  { name: 'Miami Dolphins', abbreviation: 'MIA', conference: 'AFC', division: 'East' },
  { name: 'New England Patriots', abbreviation: 'NE', conference: 'AFC', division: 'East' },
  { name: 'New York Jets', abbreviation: 'NYJ', conference: 'AFC', division: 'East' },
  // AFC West
  { name: 'Denver Broncos', abbreviation: 'DEN', conference: 'AFC', division: 'West' },
  { name: 'Kansas City Chiefs', abbreviation: 'KC', conference: 'AFC', division: 'West' },
  { name: 'Las Vegas Raiders', abbreviation: 'LV', conference: 'AFC', division: 'West' },
  { name: 'Los Angeles Chargers', abbreviation: 'LAC', conference: 'AFC', division: 'West' },
  // NFC North
  { name: 'Chicago Bears', abbreviation: 'CHI', conference: 'NFC', division: 'North' },
  { name: 'Detroit Lions', abbreviation: 'DET', conference: 'NFC', division: 'North' },
  { name: 'Green Bay Packers', abbreviation: 'GB', conference: 'NFC', division: 'North' },
  { name: 'Minnesota Vikings', abbreviation: 'MIN', conference: 'NFC', division: 'North' },
  // NFC South
  { name: 'Atlanta Falcons', abbreviation: 'ATL', conference: 'NFC', division: 'South' },
  { name: 'Carolina Panthers', abbreviation: 'CAR', conference: 'NFC', division: 'South' },
  { name: 'New Orleans Saints', abbreviation: 'NO', conference: 'NFC', division: 'South' },
  { name: 'Tampa Bay Buccaneers', abbreviation: 'TB', conference: 'NFC', division: 'South' },
  // NFC East
  { name: 'Dallas Cowboys', abbreviation: 'DAL', conference: 'NFC', division: 'East' },
  { name: 'New York Giants', abbreviation: 'NYG', conference: 'NFC', division: 'East' },
  { name: 'Philadelphia Eagles', abbreviation: 'PHI', conference: 'NFC', division: 'East' },
  { name: 'Washington Commanders', abbreviation: 'WAS', conference: 'NFC', division: 'East' },
  // NFC West
  { name: 'Arizona Cardinals', abbreviation: 'ARI', conference: 'NFC', division: 'West' },
  { name: 'Los Angeles Rams', abbreviation: 'LAR', conference: 'NFC', division: 'West' },
  { name: 'San Francisco 49ers', abbreviation: 'SF', conference: 'NFC', division: 'West' },
  { name: 'Seattle Seahawks', abbreviation: 'SEA', conference: 'NFC', division: 'West' },
].sort((a, b) => a.name.localeCompare(b.name)); // Sort teams alphabetically

function App() {
  const [awayTeam, setAwayTeam] = useState<NFLTeam | null>(null);
  const [homeTeam, setHomeTeam] = useState<NFLTeam | null>(null);

  return (
    <div className="container">
      <h1>NFL Game Matchup</h1>
      
      <div className="team-selection">
        <div className="team-selector">
          <h2>Away Team</h2>
          <select 
            value={awayTeam?.abbreviation || ''} 
            onChange={(e) => {
              const selected = NFL_TEAMS.find(team => team.abbreviation === e.target.value);
              setAwayTeam(selected || null);
            }}
            className="team-dropdown"
          >
            <option value="">Select Away Team</option>
            {NFL_TEAMS.map(team => (
              <option 
                key={team.abbreviation} 
                value={team.abbreviation}
                disabled={team === homeTeam}
              >
                {team.name}
              </option>
            ))}
          </select>
        </div>

        <div className="vs-divider">VS</div>

        <div className="team-selector">
          <h2>Home Team</h2>
          <select 
            value={homeTeam?.abbreviation || ''} 
            onChange={(e) => {
              const selected = NFL_TEAMS.find(team => team.abbreviation === e.target.value);
              setHomeTeam(selected || null);
            }}
            className="team-dropdown"
          >
            <option value="">Select Home Team</option>
            {NFL_TEAMS.map(team => (
              <option 
                key={team.abbreviation} 
                value={team.abbreviation}
                disabled={team === awayTeam}
              >
                {team.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {awayTeam && homeTeam && (
        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <h3>Selected Matchup</h3>
          <div>{awayTeam.name} @ {homeTeam.name}</div>
        </div>
      )}
    </div>
  );
}

export default App
