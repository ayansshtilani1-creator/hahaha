"""
NBA GM Simulator - Core Game Engine
Manages game state, phases, and overall simulation.
"""

import random
from typing import List, Tuple
from roster import Team, RosterFactory, Position, Player
from salary_cap import SalaryCap
from events import EventGenerator, Event
from narration import Narrator
from decisions import DecisionGenerator, Decision
import time


class GameEngine:
    """Core game engine that drives the simulation."""
    
    PHASES = ["free_agency", "training_camp", "regular_season", "trade_deadline", "playoffs"]
    
    def __init__(self, team: str = "Lakers", difficulty: str = "standard"):
        self.team = self._create_team(team)
        self.difficulty = difficulty
        self.salary_cap = SalaryCap(self.team, difficulty)
        self.event_generator = EventGenerator(self.team)
        self.narrator = Narrator(self.team)
        self.decision_generator = DecisionGenerator(self.team, "free_agency")
        
        self.current_phase = 0
        self.season_year = 2025
        self.games_played = 0
        self.decision_history = []
    
    def _create_team(self, team_name: str) -> Team:
        """Create a team with initial roster."""
        team = RosterFactory.create_rebuilding_roster(team_name)
        team.season = 2025
        
        team_cities = {
            "Knicks": ("New York", "Madison Square Garden"),
            "Lakers": ("Los Angeles", "Crypto.com Arena"),
            "Bulls": ("Chicago", "United Center"),
            "Celtics": ("Boston", "TD Garden"),
            "Heat": ("Miami", "FTX Arena"),
            "Mavericks": ("Dallas", "American Airlines Center"),
        }
        
        if team_name in team_cities:
            city, arena = team_cities[team_name]
            team.city = city
            team.arena = arena
            team.name = team_name
        
        team.update_cap_space()
        return team
    
    def start_season(self):
        """Begin the season simulation."""
        print(self.narrator.opening_scene())
        input("\n[Press ENTER to continue...]\")
        
        for phase_idx, phase in enumerate(self.PHASES):
            self.current_phase = phase_idx
            self._run_phase(phase)
            
            if phase_idx < len(self.PHASES) - 1:
                input(f"\n[Press ENTER to advance to next phase...]\")
    
    def _run_phase(self, phase: str):
        """Run a game phase."""
        print(self.narrator.phase_transition(phase))
        
        self.decision_generator.phase = phase
        
        if phase == "free_agency":
            self._run_free_agency()
        elif phase == "training_camp":
            self._run_training_camp()
        elif phase == "regular_season":
            self._run_regular_season()
        elif phase == "trade_deadline":
            self._run_trade_deadline()
        elif phase == "playoffs":
            self._run_playoffs()
    
    # ==================== PHASE IMPLEMENTATIONS ====================
    
    def _run_free_agency(self):
        """Run free agency phase."""
        print(self.team.roster_summary())
        print(f"\nCap Space Available: ${self.team.salary_cap_space:.1f}M\n")
        
        free_agents = self._generate_free_agents(8)
        
        print("AVAILABLE FREE AGENTS:\n")
        for i, fa in enumerate(free_agents, 1):
            print(f"{i}. {fa.name:<20} | {fa.position.value:<15} | OVR {fa.overall_rating}/99 | ${fa.contract.annual_salary:.1f}M")
        
        print("\n" + "="*70)
        
        decisions = self.decision_generator.get_random_decisions(2)
        for decision in decisions:
            self._present_decision(decision)
        
        # Simple FA signing
        print("\nWould you like to sign any free agents? (Type player number or 'skip')")
        choice = input(">>> ").strip().lower()
        
        if choice != "skip" and choice.isdigit():
            fa_idx = int(choice) - 1
            if 0 <= fa_idx < len(free_agents):
                fa = free_agents[fa_idx]
                success, msg = self.salary_cap.sign_player(fa)
                print(msg)
                if success:
                    print(self.narrator.headline(f"Breaking: {fa.name} signs with {self.team}")
                    print(self.narrator.player_quote(fa, "positive"))
        
        print(self.team.roster_summary())
        self.team.reputation = min(100, self.team.reputation + random.randint(-2, 3))
    
    def _run_training_camp(self):
        """Run training camp phase."""
        print(f"Training Camp for the {self.team} begins.\n")
        print(self.team.roster_summary())
        
        # Generate events
        events = self.event_generator.generate_event_batch(1)
        for event in events:
            self._present_event(event)
        
        decisions = self.decision_generator.get_random_decisions(2)
        for decision in decisions:
            self._present_decision(decision)
        
        print(f"\nCurrent Reputation: {self.team.reputation}/100")
    
    def _run_regular_season(self):
        """Run regular season phase."""
        print(f"The {self.season_year}-{self.season_year + 1} Regular Season is underway.\n")
        
        # Simulate 82 games in chunks
        for week in range(1, 20):  # ~20 weeks, 4 games per week
            self.games_played += 4;
            
            # Random wins/losses
            wins = random.randint(1, 4);
            self.team.wins += wins;
            self.team.losses += (4 - wins);
            
            print(f"Week {week}: Games played: {self.games_played} | Record: {self.team.record()}");
            
            # Occasional events
            if random.random() < 0.3:
                event = self.event_generator.generate_random_event();
                self._present_event(event);
            
            # Occasional decision
            if random.random() < 0.15:
                decision = random.choice(self.decision_generator.get_random_decisions(1));
                self._present_decision(decision);
        
        print(f"\nRegular Season Complete: {self.team.record()}");
        print(self.narrator.game_summary(self.team.wins, self.team.losses, self.team.get_average_rating()));
    
    def _run_trade_deadline(self):
        """Run trade deadline phase."""
        print(f"Trade Deadline: 48 hours remaining.\n");
        
        decisions = self.decision_generator.get_random_decisions(2);
        for decision in decisions:
            self._present_decision(decision);
        
        print(f"\nTrade Deadline has passed. Rosters are now locked.");
    
    def _run_playoffs(self):
        """Run playoff phase."""
        print(f"Playoff Seeding: TBD\n");
        
        if self.team.wins > self.team.losses:
            print(f"✓ The {self.team} have made the playoffs!");
            self.team.playoff_seed = random.randint(6, 8);
            
            # Playoff games
            for round_num in range(1, 4):
                print(f"\nPlayoff Round {round_num}...");
                series_won = random.random() > 0.4;
                if series_won:
                    print(f"✓ Series won! Advancing...");
                else:
                    print(f"✗ Series lost. Playoff run ends.");
                    break;
        else:
            print(f"The {self.team} missed the playoffs. Lottery awaits.");
            self.team.draft_picks = [1] + self.team.draft_picks;
        
        print(self.narrator.season_end_summary(self.team.record(), self.team.playoff_seed is not None, self.team.reputation));
    
    # ==================== HELPER METHODS ====================
    
    def _present_event(self, event: Event):
        """Present and process an event."""
        print(f"\n{'='*70}");
        print(f"  {event.title}");
        print(f"{'='*70}");
        print(f"\n{event.description}\n");
        
        self.event_generator.apply_event_effects(event);
        
        print(f"[Impact: {event.impact.upper()} | Reputation: {event.reputation_change:+d}]\n");
    
    def _present_decision(self, decision: Decision):
        """Present decision and process choice."""
        print(f"\n{'='*70}");
        print(f"  DECISION: {decision.title}");
        print(f"{'='*70}\n");
        print(f"{decision.scenario}\n");
        
        for letter, title, desc in decision.options:
            print(f"[{letter}] {title}");
            print(f"    {desc}\n");
        
        choice = input("Your choice (A/B/C): ").strip().upper();
        
        if choice not in ["A", "B", "C"]:
            print("Invalid choice. Defaulting to A...");
            choice = "A";
        
        choice_idx = ord(choice) - ord("A");
        consequence = decision.consequences[choice_idx];
        reputation_delta = decision.reputation_deltas[choice_idx];
        
        print(self.narrator.consequence_narration(
            f"You chose: {decision.options[choice_idx][1]}",
            consequence,
            reputation_delta
        ));
        
        self.team.reputation = max(0, min(100, self.team.reputation + reputation_delta));
        self.decision_history.append((decision.title, choice));
    
    def _generate_free_agents(self, count: int = 5) -> List[Player]:
        """Generate a pool of free agents."""
        free_agents = [];
        for _ in range(count):
            pos = random.choice(list(Position));
            player = RosterFactory.generate_player(pos);
            player.contract.years_remaining = 1  # All FAs in year 1
            free_agents.append(player);
        return free_agents;
    
    def get_game_state(self) -> dict:
        """Get current game state."""
        return {
            "team": str(self.team),
            "record": self.team.record(),
            "reputation": self.team.reputation,
            "payroll": self.team.get_total_payroll(),
            "cap_space": self.team.salary_cap_space,
            "phase": self.PHASES[self.current_phase],
            "games_played": self.games_played,
        }