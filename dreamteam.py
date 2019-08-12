from collections import defaultdict
from itertools import combinations, product
from requests import get

class DreamTeam:
    min_price_goalie = 40
    min_price_defender = 40
    min_price_midfielder = 45
    min_price_forward = 45
    total_goalie_count = 2
    total_defender_count = 5
    total_midfielder_count = 5
    total_forward_count = 3
    valid_formations = ((1, 3, 4, 3), (1, 3, 5, 2), (1, 4, 3, 3), (1, 4, 4, 2), (1, 4, 5, 1), (1, 5, 3, 2), (1, 5, 4, 1))

    def __init__(self):        
        self.url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
        self.goalkeepers = []
        self.defenders = []
        self.midfielders = []
        self.forwards = []

    def part_selections(self, player_dict, count):
        valid = []

        for price_spread in range(1, count + 1):
            for c in combinations(player_dict.values(), price_spread):
                if price_spread == 1:
                    valid.append(c[0][:count])
                elif price_spread == count:
                    valid.append([l[0] for l in c])
                elif count - price_spread == 1:
                    for i in range(price_spread):
                        if len(c[i]) < 2:
                            continue
                        valid.append([l[0] for l in c] + [c[i][1]])
                elif price_spread == 2 and count == 4:
                    valid.append(c[0][:1] + c[1][:3])
                    valid.append(c[0][:2] + c[1][:2])
                    valid.append(c[0][:3] + c[1][:1])
                elif price_spread == 3 and count == 5:
                    valid.append(c[0][:1] + c[1][:1] + c[2][:3])
                    valid.append(c[0][:1] + c[1][:2] + c[2][:2])
                    valid.append(c[0][:1] + c[1][:3] + c[2][:1])
                    valid.append(c[0][:2] + c[1][:1] + c[2][:2])
                    valid.append(c[0][:2] + c[1][:2] + c[2][:1])
                    valid.append(c[0][:3] + c[1][:1] + c[2][:1])
                elif price_spread == 2 and count == 5:
                    valid.append(c[0][:1] + c[1][:4])
                    valid.append(c[0][:2] + c[1][:3])
                    valid.append(c[0][:3] + c[1][:2])
                    valid.append(c[0][:4] + c[1][:1])
                    
        return [v for v in valid if len(v) == count]

    def build_dream_team(self):
        def build(gk_count, def_count, mid_count, for_count):
            base_budget = 1000 - (DreamTeam.total_goalie_count - gk_count) * DreamTeam.min_price_goalie - (DreamTeam.total_defender_count - def_count) * DreamTeam.min_price_defender - (DreamTeam.total_midfielder_count - mid_count) * DreamTeam.min_price_midfielder - (DreamTeam.total_forward_count - for_count) * DreamTeam.min_price_forward
            best = 0
            best_xi = []

            goalkeepers_by_cost = defaultdict(list)
            defenders_by_cost = defaultdict(list)
            midfielders_by_cost = defaultdict(list)
            attackers_by_cost = defaultdict(list)

            for gk in self.goalkeepers:
                goalkeepers_by_cost[gk['now_cost']].append(gk)
            for df in self.defenders:
                defenders_by_cost[df['now_cost']].append(df)
            for mf in self.midfielders:
                midfielders_by_cost[mf['now_cost']].append(mf)
            for fw in self.forwards:
                attackers_by_cost[fw['now_cost']].append(fw)

            for _, v in goalkeepers_by_cost.items():
                v.sort(key=lambda player: -player['event_points'])
            for _, v in defenders_by_cost.items():
                v.sort(key=lambda player: -player['event_points'])
            for _, v in midfielders_by_cost.items():
                v.sort(key=lambda player: -player['event_points'])
            for _, v in attackers_by_cost.items():
                v.sort(key=lambda player: -player['event_points'])

            goalkeeper_selections = self.part_selections(goalkeepers_by_cost, gk_count)
            defender_selections = self.part_selections(defenders_by_cost, def_count)
            midfielder_selections = self.part_selections(midfielders_by_cost, mid_count)
            forward_selections = self.part_selections(attackers_by_cost, for_count)

            for p in product(goalkeeper_selections, defender_selections, midfielder_selections, forward_selections):
                team = [player for part in p for player in part]
                selection_cost = sum(player['now_cost'] for player in team)
                point_total = sum(player['event_points'] for player in team) + max(player['event_points'] for player in team)
                team_counts = defaultdict(int)

                for part in p:
                    for player in part:
                        team_counts[player['team']] += 1

                if selection_cost <= base_budget and point_total > best and max(team_counts.values()) <= 3:
                    best = point_total
                    best_xi = p[0] + p[1] + p[2] + p[3]

            print(best, [p['first_name'] + ' ' + p['second_name'] for p in best_xi])
            return best, best_xi

        results = [build(*formation) for formation in DreamTeam.valid_formations]
        return [result for result in results if result[0] == max(r[0] for r in results)][0]

    def get_best(self):
        data = {}

        if True:
            from json import load
            with open('C:\\Users\\chris\\OneDrive\\Dokument\\Python\\fpl\\data.json', encoding='utf-8') as f:
                data = load(f)
        else:
            response = get(self.url)
            data = response.json()
        
        players = data['elements']

        for player in players:
            player_type = player['element_type']
            
            if player_type == 1:
                self.goalkeepers.append(player)
            elif player_type == 2:
                self.defenders.append(player)
            elif player_type == 3:
                self.midfielders.append(player)
            elif player_type == 4:
                self.forwards.append(player)

        return self.build_dream_team()

if __name__ == '__main__':
    dt = DreamTeam()
    dt.get_best()