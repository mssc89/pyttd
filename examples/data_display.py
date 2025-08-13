#!/usr/bin/env python3
"""
Data Display - Complete OpenTTD Game State Monitor
================================================================

This example demonstrates how to retrieve and display all available 
real-time game state data from an OpenTTD server, matching what's 
shown in the OpenTTD GUI.

Features Demonstrated:
- Real-time game date and calendar information
- Complete company and client listings
- Financial data for all companies
- Server configuration and map information  
- Vehicle statistics and tracking
- Economic indicators and performance metrics

Usage:
    python examples/data_display.py
"""

import time
import logging
import uuid
import sys
import os

# Add the parent directory to the path to import pyttd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyttd import OpenTTDClient

# Set up clean logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Reduce protocol noise for cleaner output
logging.getLogger('pyttd.protocol').setLevel(logging.WARNING)
logging.getLogger('pyttd.connection').setLevel(logging.WARNING)


class OpenTTDDataMonitor:
    """OpenTTD game state data monitor"""
    
    def __init__(self, server="127.0.0.1", port=3979):
        self.unique_id = str(uuid.uuid4())[:8]
        self.client = OpenTTDClient(
            server=server,
            port=port,
            player_name=f"DataMonitor_{self.unique_id}",
            company_name=f"MonitorCorp_{self.unique_id}"
        )
        
    def connect_and_monitor(self):
        """Connect to server and start monitoring"""
        logger.info("Connecting to OpenTTD server...")
        
        # Set up event handlers
        self.client.on('game_joined', self.on_game_joined)
        
        # Track if we've shown initial display
        self._displayed_initial_data = False
        
        success = self.client.connect()
        if not success:
            logger.error("Failed to connect to server")
            return False
            
        logger.info("Connected successfully!")
        return True
        
    def on_game_joined(self):
        """Called when we successfully join the game"""
        logger.info("Joined game! Starting data collection...")
        
        # Request game info immediately after joining to avoid timeout
        logger.info("Requesting game info immediately to avoid server timeout...")
        self.client.request_game_info()
        
        # Wait briefly for the response
        max_wait = 5  # Short wait to avoid server timeout
        wait_interval = 0.2  # Check every 200ms
        waited = 0
        
        while waited < max_wait:
            time.sleep(wait_interval)
            waited += wait_interval
            
            # Check if we have received real game data
            if hasattr(self.client, '_real_game_data') and self.client._real_game_data:
                logger.info(f"Real game data received after {waited:.1f} seconds!")
                break
        else:
            logger.info("Using available data (real-time server data may arrive later)")
        
        # Display all available data
        self.display_comprehensive_data()
        self._displayed_initial_data = True
        
        # Send summary to chat  
        self.broadcast_data_summary()
        
        # If we didn't get real data, try once more after a short delay
        if not (hasattr(self.client, '_real_game_data') and self.client._real_game_data):
            logger.info("Attempting one more request for complete server data...")
            time.sleep(2)
            self.client.request_game_info()
            time.sleep(1)
            
            if hasattr(self.client, '_real_game_data') and self.client._real_game_data:
                logger.info("Updated game data received! Displaying refreshed data...")
                self.display_comprehensive_data()
        
    def display_comprehensive_data(self):
        """Display all available game state data"""
        print("\n" + "=" * 80)
        print("OPENTTD GAME STATE DATA")
        print("=" * 80)
        
        # 1. Server and Connection Information
        self.display_server_info()
        
        # 2. Game Calendar and Time
        self.display_calendar_info()
        
        # 3. Map Information
        self.display_map_info()
        
        # 4. Company Information
        self.display_company_info()
        
        # 5. Client Information
        self.display_client_info()
        
        # 6. Financial Analysis
        self.display_financial_info()
        
        # 7. Vehicle Information
        self.display_vehicle_info()
        
        # 8. Station and Infrastructure Data
        self.display_station_info()
        
        # 9. Industry Information
        self.display_industry_info()
        
        # 10. Economic Indicators
        self.display_economic_info()
        
        # 11. Performance Metrics
        self.display_performance_info()
        
        print("=" * 80)
        print("Data collection completed!")
        print("=" * 80 + "\n")
        
    def display_server_info(self):
        """Display server configuration and connection details"""
        print("\nSERVER INFORMATION")
        print("-" * 50)
        
        game_info = self.client.get_game_info()
        
        print(f"Server Name: {game_info.get('server_name', 'Unknown')}")
        print(f"Client ID: {game_info.get('client_id', 'Unknown')}")
        print(f"Connection Status: {game_info.get('status', 'Unknown')}")
        print(f"Game Synchronized: {game_info.get('synchronized', False)}")
        
        # Show real-time data availability - check if we have current game data
        has_real_data = hasattr(self.client, '_real_game_data') and self.client._real_game_data
        print(f"Real-time Data Available: {'Yes' if has_real_data else 'No'}")
        
    def display_calendar_info(self):
        """Display game calendar and time information"""
        print("\nCALENDAR & TIME INFORMATION")
        print("-" * 50)
        
        game_info = self.client.get_game_info()
        
        current_year = game_info.get('current_year', 'Unknown')
        start_year = game_info.get('start_year', 'Unknown')
        ticks_playing = game_info.get('ticks_playing', 0)
        
        print(f"Current Game Year: {current_year}")
        print(f"Game Started Year: {start_year}")
        if isinstance(current_year, int) and isinstance(start_year, int):
            years_playing = current_year - start_year
            print(f"Years Playing: {years_playing}")
        
        print(f"Game Ticks: {ticks_playing:,}" if isinstance(ticks_playing, int) else f"Game Ticks: {ticks_playing}")
        print(f"Calendar Date ID: {game_info.get('calendar_date', 'Unknown')}")
        
    def display_map_info(self):
        """Display map size and terrain information"""
        print("\nMAP INFORMATION")
        print("-" * 50)
        
        game_info = self.client.get_game_info()
        map_info = self.client.get_map_info()
        
        print(f"Map Size: {game_info.get('map_size', 'Unknown')}")
        
        if map_info:
            print(f"Map Width: {map_info.get('size_x', 'Unknown')}")
            print(f"Map Height: {map_info.get('size_y', 'Unknown')}")
            if 'landscape' in map_info:
                landscapes = {0: 'Temperate', 1: 'Arctic', 2: 'Tropical', 3: 'Toyland'}
                landscape_name = landscapes.get(map_info['landscape'], f"Unknown ({map_info['landscape']})")
                print(f"Landscape: {landscape_name}")
            if 'seed' in map_info:
                print(f"Map Seed: {map_info['seed']}")
                
    def display_company_info(self):
        """Display company information"""
        print("\nCOMPANY INFORMATION")
        print("-" * 50)
        
        game_info = self.client.get_game_info()
        companies = self.client.get_companies()
        
        # Summary - use real game data for accurate counts
        companies_active = game_info.get('companies', len(companies))
        companies_max = game_info.get('companies_max', 'Unknown')
        print(f"Active Companies: {companies_active}/{companies_max}")
        
        # Our company
        our_company = self.client.get_our_company()
        our_company_id = self.client.game_state.company_id
        
        if our_company_id != 255:  # Not spectator
            print(f"Our Company ID: {our_company_id}")
            if our_company:
                print(f"Our Company Name: {getattr(our_company, 'name', 'Unknown')}")
        else:
            print("Status: Spectator")
            
        # Detailed company list - show what we have tracked, but note the limitation
        if companies:
            print(f"\nDetailed Company List ({len(companies)} tracked):")
            for company_id, company_data in companies.items():
                name = company_data.get('name', f'Company {company_id}')
                manager = company_data.get('manager_name', 'Unknown')
                is_ai = company_data.get('is_ai', False)
                company_type = 'AI' if is_ai else 'Human'
                print(f"  {company_type} Company {company_id}: {name} (Manager: {manager})")
        else:
            print("No detailed company data available")
            
        # Note about AI companies
        if companies_active > len(companies):
            missing_companies = companies_active - len(companies)
            print(f"\nNote: {missing_companies} additional companies exist (likely AI companies)")
            print("Detailed information for AI companies requires admin protocol or map parsing")
            
    def display_client_info(self):
        """Display client connection information"""
        print("\nCLIENT INFORMATION")
        print("-" * 50)
        
        game_info = self.client.get_game_info()
        clients = self.client.get_clients()
        
        # Summary
        clients_active = game_info.get('clients', len(clients))
        clients_max = game_info.get('clients_max', 'Unknown')
        spectators = game_info.get('spectators', 'Unknown')
        
        print(f"Connected Clients: {clients_active}/{clients_max}")
        print(f"Spectators: {spectators}")
        
        # Detailed client list
        if clients:
            print(f"\nDetailed Client List ({len(clients)} tracked):")
            for client_id, client_data in clients.items():
                name = client_data.get('name', f'Client {client_id}')
                company_id = client_data.get('company_id', 'Unknown')
                
                if company_id == 255:
                    status = "Spectator"
                elif company_id == 254:
                    status = "Creating Company"
                else:
                    status = f"Company {company_id}"
                    
                print(f"  Client {client_id}: {name} ({status})")
        else:
            print("No detailed client data available")
            
    def display_financial_info(self):
        """Display financial information and company finances"""
        print("\nFINANCIAL INFORMATION")
        print("-" * 50)
        
        # Our company finances
        finances = self.client.get_company_finances()
        if finances:
            print("Our Company Finances:")
            for key, value in finances.items():
                if isinstance(value, (int, float)):
                    if 'rate' in key.lower() or 'ratio' in key.lower():
                        print(f"  {key.replace('_', ' ').title()}: {value:.1f}{'%' if 'rate' in key.lower() else ''}")
                    elif key.lower() in ['company_id', 'inaugurated_year', 'bankrupt_counter', 'is_ai']:
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: £{value:,}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print("No personal financial data available (may be spectator)")
            
        # Performance data
        performance = self.client.get_company_performance()
        if performance:
            print("\nCompany Performance:")
            for key, value in performance.items():
                if isinstance(value, (int, float)):
                    if 'value' in key.lower() or 'money' in key.lower() or 'worth' in key.lower():
                        print(f"  {key.replace('_', ' ').title()}: £{value:,}")
                    elif 'rate' in key.lower() or 'rating' in key.lower():
                        print(f"  {key.replace('_', ' ').title()}: {value}{'%' if 'rate' in key.lower() else ''}")
                    elif key.lower() in ['age_years', 'loan']:
                        if key.lower() == 'loan':
                            print(f"  {key.replace('_', ' ').title()}: £{value:,}")
                        else:
                            print(f"  {key.replace('_', ' ').title()}: {value}")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
                    
    def display_vehicle_info(self):
        """Display comprehensive vehicle statistics and information"""
        print("\nVEHICLE INFORMATION")
        print("-" * 50)
        
        # Try to get comprehensive vehicle data from map parsing
        comprehensive_stats = self.client.get_comprehensive_vehicle_statistics()
        map_vehicles = self.client.get_all_vehicles_from_map()
        
        # Display total vehicle count
        total_vehicles = comprehensive_stats.get('total_vehicles', 0)
        if total_vehicles > 0:
            print(f"Total Vehicles in Game: {total_vehicles} (from map data)")
        else:
            # Fallback to estimation
            estimated_total = self.client.get_total_vehicle_count()
            tracked_vehicles = len(self.client.game_state.vehicles)
            
            if estimated_total > tracked_vehicles:
                print(f"Total Vehicles in Game: ~{estimated_total} (estimated)")
                print(f"Tracked Vehicles: {tracked_vehicles}")
            else:
                print(f"Total Vehicles in Game: {tracked_vehicles}")
        
        # Our vehicles
        our_vehicles = self.client.get_our_vehicles()
        print(f"Our Vehicles: {len(our_vehicles)}")
        
        if our_vehicles:
            print("Our Vehicle List:")
            for vehicle_id, vehicle_data in our_vehicles.items():
                vehicle_type = vehicle_data.get('type', 'Unknown')
                vehicle_name = vehicle_data.get('name', f'Vehicle {vehicle_id}')
                print(f"  {vehicle_type} {vehicle_id}: {vehicle_name}")
        
        # Comprehensive vehicle statistics
        print("\nVehicle Statistics:")
        for key, value in comprehensive_stats.items():
            if isinstance(value, dict):
                print(f"  {key.replace('_', ' ').title()}:")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict):
                        # Handle nested company data
                        print(f"    {sub_key.replace('_', ' ').title()}:")
                        for company_id, count in sub_value.items():
                            print(f"      Company {company_id}: {count} vehicles")
                    else:
                        print(f"    {sub_key}: {sub_value}")
            else:
                if isinstance(value, (int, float)) and 'profit' in key.lower():
                    print(f"  {key.replace('_', ' ').title()}: £{value:,}")
                elif 'year' in key.lower():
                    print(f"  {key.replace('_', ' ').title()}: {value}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Additional map-based vehicle information
        if map_vehicles:
            print(f"\nDetailed Vehicle Data (from map): {len(map_vehicles)} vehicles found")
            
            # Group by company for summary
            company_vehicles = {}
            for vehicle in map_vehicles:
                company_id = vehicle.get('company_id', 0)
                if company_id not in company_vehicles:
                    company_vehicles[company_id] = []
                company_vehicles[company_id].append(vehicle)
            
            for company_id, vehicles in company_vehicles.items():
                print(f"  Company {company_id}: {len(vehicles)} vehicles")
                
                # Show vehicle type breakdown
                type_counts = {"train": 0, "road": 0, "ship": 0, "aircraft": 0}
                for vehicle in vehicles:
                    vtype = vehicle.get('vehicle_type', 0)
                    if vtype == 0:
                        type_counts["train"] += 1
                    elif vtype == 1:
                        type_counts["road"] += 1
                    elif vtype == 2:
                        type_counts["ship"] += 1
                    elif vtype == 3:
                        type_counts["aircraft"] += 1
                
                type_summary = ", ".join([f"{count} {vtype}" for vtype, count in type_counts.items() if count > 0])
                if type_summary:
                    print(f"    Types: {type_summary}")
        else:
            print("\nNote: Detailed vehicle data requires map parsing")
                        
    def display_station_info(self):
        """Display station and infrastructure information"""
        print("\nSTATION & INFRASTRUCTURE INFORMATION")
        print("-" * 50)
        
        # Get station data from map parsing
        stations = self.client.get_all_stations_from_map()
        
        if stations:
            print(f"Total Stations: {len(stations)}")
            
            # Group stations by company
            company_stations = {}
            for station in stations:
                company_id = station.get('company_id', 0)
                if company_id not in company_stations:
                    company_stations[company_id] = []
                company_stations[company_id].append(station)
            
            print("\nStations by Company:")
            for company_id, company_stations_list in company_stations.items():
                print(f"  Company {company_id}: {len(company_stations_list)} stations")
                
                # Show sample stations
                for i, station in enumerate(company_stations_list[:3]):  # Show first 3
                    name = station.get('name', f'Station {station.get("station_id", i)}')
                    facilities = station.get('facilities', 0)
                    
                    # Decode facility types (simplified)
                    facility_types = []
                    if facilities & 1: facility_types.append("Rail")
                    if facilities & 2: facility_types.append("Airport") 
                    if facilities & 4: facility_types.append("Truck")
                    if facilities & 8: facility_types.append("Bus")
                    if facilities & 16: facility_types.append("Dock")
                    
                    facility_str = ", ".join(facility_types) if facility_types else "Unknown"
                    print(f"    {name} ({facility_str})")
                
                if len(company_stations_list) > 3:
                    print(f"    ... and {len(company_stations_list) - 3} more stations")
        else:
            print("Total Stations: Unknown (requires map parsing)")
            print("\nNote: Station data is available through map parsing")
            print("Enable detailed map parsing to see station information")

    def display_industry_info(self):
        """Display industry and economy information"""
        print("\nINDUSTRY INFORMATION")
        print("-" * 50)
        
        # Get industry data from map parsing
        industries = self.client.get_all_industries_from_map()
        
        if industries:
            print(f"Total Industries: {len(industries)}")
            
            # Group industries by type
            industry_types = {}
            for industry in industries:
                industry_type = industry.get('industry_type', 0)
                type_name = industry.get('name', f'Industry Type {industry_type}')
                if type_name not in industry_types:
                    industry_types[type_name] = 0
                industry_types[type_name] += 1
            
            print("\nIndustries by Type:")
            for industry_name, count in industry_types.items():
                print(f"  {industry_name}: {count}")
            
            # Show production information for sample industries
            print(f"\nSample Industry Details:")
            for i, industry in enumerate(industries[:5]):  # Show first 5
                name = industry.get('name', f'Industry {i}')
                production = industry.get('last_month_production', [])
                accepts = industry.get('accepts_cargo', [])
                produces = industry.get('produces_cargo', [])
                
                print(f"  {name}")
                if production:
                    print(f"    Production: {production}")
                if accepts:
                    print(f"    Accepts: Cargo types {accepts}")
                if produces:
                    print(f"    Produces: Cargo types {produces}")
            
            if len(industries) > 5:
                print(f"  ... and {len(industries) - 5} more industries")
        else:
            print("Total Industries: Unknown (requires map parsing)")
            print("\nNote: Industry data is available through map parsing")
            print("Enable detailed map parsing to see:")
            print("  - Industry production rates")
            print("  - Cargo acceptance and production")
            print("  - Industry locations and types")
                        
    def display_economic_info(self):
        """Display economic indicators and market information"""
        print("\nECONOMIC INFORMATION")
        print("-" * 50)
        
        economic_status = self.client.get_economic_status()
        if economic_status:
            print("Economic Indicators:")
            for key, value in economic_status.items():
                if isinstance(value, (int, float)):
                    if 'rate' in key.lower():
                        print(f"  {key.replace('_', ' ').title()}: {value}%")
                    elif 'loan' in key.lower() or 'money' in key.lower():
                        print(f"  {key.replace('_', ' ').title()}: £{value:,}")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print("No economic data available")
            
        # Loan interest calculation
        try:
            interest = self.client.calculate_loan_interest()
            print(f"Current Loan Interest (Annual): £{interest:,}")
        except:
            print("Loan interest calculation unavailable")
            
    def display_performance_info(self):
        """Display performance metrics and game statistics"""
        print("\nPERFORMANCE METRICS")
        print("-" * 50)
        
        # Check if we can afford various things
        test_amounts = [10000, 50000, 100000, 500000, 1000000]
        print("Affordability Analysis:")
        for amount in test_amounts:
            can_afford = self.client.can_afford(amount)
            status = "Affordable" if can_afford else "Too expensive"
            print(f"  £{amount:,}: {status}")
            
        # Construction cost estimates
        print("\nConstruction Cost Estimates:")
        try:
            rail_cost = self.client.estimate_construction_cost((10, 10), (20, 20), "rail")
            print(f"  Rail (10,10) to (20,20): £{rail_cost:,}")
        except:
            print("  Rail cost estimation unavailable")
            
        # Auto-management recommendation
        try:
            auto_mgmt = self.client.auto_manage_company()
            if auto_mgmt and isinstance(auto_mgmt, dict):
                print(f"\nAI Recommendation: {auto_mgmt.get('recommendation', 'None')}")
                if 'actions_taken' in auto_mgmt:
                    actions = auto_mgmt['actions_taken']
                    if actions:
                        print("Suggested Actions:")
                        for action in actions:
                            print(f"  - {action}")
        except:
            print("\nAuto-management analysis unavailable")
            
    def broadcast_data_summary(self):
        """Send a summary of key data to game chat"""
        game_info = self.client.get_game_info()
        
        # Create concise summary
        year = game_info.get('current_year', '?')
        companies = game_info.get('companies', '?')
        clients = game_info.get('clients', '?')
        
        summary = f"Game Data: Year {year}, {companies} companies, {clients} clients connected"
        self.client.send_chat(summary)
        
    def run(self, duration=30):
        """Run the data monitor for specified duration"""
        try:
            if not self.connect_and_monitor():
                return
                
            logger.info(f"Monitoring for {duration} seconds...")
            
            # Keep connection alive and check for real game data updates
            start_time = time.time()
            last_real_data_check = False
            
            while self.client.is_connected() and (time.time() - start_time) < duration:
                time.sleep(1)
                
                # Check if real game data has arrived and we haven't displayed it yet
                has_real_data = hasattr(self.client, '_real_game_data') and self.client._real_game_data
                if has_real_data and not last_real_data_check and self._displayed_initial_data:
                    logger.info("Real-time server data received! Displaying updated information...")
                    self.display_comprehensive_data()
                    last_real_data_check = True
                
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
        finally:
            if self.client.is_connected():
                logger.info("Disconnecting...")
                self.client.disconnect()
            logger.info("Data monitoring completed!")


def main():
    """Main entry point"""
    print("OpenTTD Data Display")
    print("=" * 60)
    print("This script connects to an OpenTTD server and displays")
    print("all available real-time game state information.")
    print("=" * 60 + "\n")
    
    # Create and run monitor
    monitor = OpenTTDDataMonitor()
    monitor.run(duration=30)


if __name__ == "__main__":
    main()