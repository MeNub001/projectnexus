import networkx as nx
import time

class AegisDispatcher:
    def __init__(self):
        self.G = nx.Graph()
        self._build_road_network()
        # Include all 3 critical field facilities with standard base telemetries
        self.shelters = {
            "SK Seri Iskandar": {"evacuees": 40, "hours_left": 1.2, "pi": 0.0},
            "Dewan Serbaguna Bota": {"evacuees": 60, "hours_left": 1.8, "pi": 0.0},
            "Klinik Kesihatan Seri Iskandar": {"evacuees": 25, "hours_left": 2.0, "pi": 0.0}
        }
        self.base_node = "Balai Bomba Command Hub"

    def _build_road_network(self):
        edges = [
            ("Balai Bomba Command Hub", "Simpang UTP Junction", 3.0),
            ("Balai Bomba Command Hub", "Klinik Kesihatan Seri Iskandar", 2.0),
            ("Klinik Kesihatan Seri Iskandar", "Simpang UTP Junction", 2.5),
            
            
            ("Simpang UTP Junction", "Jambatan Bota Kanan", 4.0),
            ("Jambatan Bota Kanan", "SK Seri Iskandar", 3.5),
            ("Jambatan Bota Kanan", "Dewan Serbaguna Bota", 3.0),
            
            
            ("Simpang UTP Junction", "Lebuhraya High Ground Bypass", 6.5),
            ("Lebuhraya High Ground Bypass", "SK Seri Iskandar", 5.0),
            ("Lebuhraya High Ground Bypass", "Dewan Serbaguna Bota", 7.5),
        ]
        self.G.add_weighted_edges_from(edges)

    def process_incident(self, incident: dict) -> dict:
        start_time = time.time()
        
        # 1. Road Severing / Hazard Simulation
        blocked_road = incident.get("blocked_road")
        if blocked_road and self.G.has_node(blocked_road):
            self.G.remove_node(blocked_road)
            
        # 2. Dynamic Field Telemetry Updates
        target_shelter = incident.get("shelter")
        added_evacuees = incident.get("evacuees", 0)
        critical_need = str(incident.get("critical_need", "")).lower()

        # Update targeted facility state
        if target_shelter and target_shelter in self.shelters:
            if added_evacuees > 0:
                self.shelters[target_shelter]["evacuees"] = added_evacuees
            # Critical shortage drastically reduces remaining hours
            if any(k in critical_need for k in ["oxygen", "cholera", "water", "ration"]):
                self.shelters[target_shelter]["hours_left"] = 0.5
        elif target_shelter and target_shelter not in self.shelters:
            self.shelters[target_shelter] = {
                "evacuees": added_evacuees if added_evacuees > 0 else 50,
                "hours_left": 0.5,
                "pi": 0.0
            }

        # 3. Social Equity Priority Arbitration Algorithm
        # Priority Index = (Evacuees / Hours_Left) * Medical_Weight
        rankings = []
        for name, data in self.shelters.items():
            base_ratio = data["evacuees"] / max(data["hours_left"], 0.1)
            # Give medical facilities high triage priority when critical
            weight = 2.0 if "klinik" in name.lower() and "oxygen" in critical_need else 1.0
            pi = round((base_ratio * weight) / 100.0, 3)
            data["pi"] = pi
            rankings.append({
                "shelter": name,
                "evacuees": data["evacuees"],
                "hours_left": data["hours_left"],
                "priority_index": pi
            })
            
        rankings.sort(key=lambda x: x["priority_index"], reverse=True)
        
        # Target is prioritized by the highest equity index or incoming distress call
        selected_target = target_shelter if (target_shelter and target_shelter in self.shelters) else rankings[0]["shelter"]
        
        # 4. A* Shortest Safe Trajectory Planning
        try:
            route = nx.astar_path(self.G, self.base_node, selected_target, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            route = [self.base_node, "NO REACHABLE PATH"]
            
        latency = round((time.time() - start_time) * 1000, 2)
        
        return {
            "selected_target": selected_target,
            "calculated_route": route,
            "rankings": rankings,
            "latency_ms": latency
        }