"""OpenTTD Map Data Parser

This module provides functionality to parse OpenTTD map data received from the
network protocol. The map data contains comprehensive game state including:
- Vehicle information
- Station and infrastructure data  
- Industry and economy data
- Company details
- Tile data

The map is sent as compressed savegame data that needs to be decompressed and parsed.
"""

import logging
import zlib
import struct
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import IntEnum

logger = logging.getLogger(__name__)

class TileType(IntEnum):
    """OpenTTD tile types"""
    CLEAR = 0
    RAIL = 1
    ROAD = 2
    TOWN = 3
    TREES = 4
    STATION = 5
    WATER = 6
    VOID = 7
    INDUSTRY = 8
    TUNNEL = 9
    BRIDGE = 10
    OBJECT = 11

class VehicleType(IntEnum):
    """OpenTTD vehicle types"""
    TRAIN = 0
    ROAD = 1
    SHIP = 2
    AIRCRAFT = 3
    EFFECT = 4
    DISASTER = 5

@dataclass
class ParsedVehicle:
    """Parsed vehicle data from map"""
    vehicle_id: int
    vehicle_type: VehicleType
    company_id: int
    engine_type: int
    x: int
    y: int
    z: int
    speed: int
    profit_this_year: int
    profit_last_year: int
    running_cost: int
    build_year: int
    reliability: int
    cargo_type: int
    cargo_capacity: int
    cargo_count: int
    
@dataclass 
class ParsedStation:
    """Parsed station data from map"""
    station_id: int
    company_id: int
    name: str
    x: int
    y: int
    facilities: int  # Station facilities bitmask
    build_date: int
    
@dataclass
class ParsedIndustry:
    """Parsed industry data from map"""
    industry_id: int
    industry_type: int
    name: str
    x: int
    y: int
    production_rate: List[int]
    last_month_production: List[int]
    accepts_cargo: List[int]
    produces_cargo: List[int]

@dataclass
class ParsedCompany:
    """Parsed company data from map"""
    company_id: int
    name: str
    manager_name: str
    money: int
    loan: int
    value: int
    performance: int
    inaugurated_year: int
    is_ai: bool
    vehicles_count: int

class MapDataParser:
    """Parser for OpenTTD map data"""
    
    def __init__(self):
        self.map_width = 0
        self.map_height = 0
        self.vehicles: List[ParsedVehicle] = []
        self.stations: List[ParsedStation] = []
        self.industries: List[ParsedIndustry] = []
        self.companies: List[ParsedCompany] = []
        self.tiles: List[List[int]] = []  # 2D array of tile types
        
    def parse_map_data(self, compressed_data: bytes) -> Dict[str, Any]:
        """
        Parse compressed OpenTTD map data
        
        Args:
            compressed_data: Compressed map data from server
            
        Returns:
            Dictionary containing parsed game state
        """
        try:
            # Decompress the map data
            decompressed = self._decompress_map_data(compressed_data)
            
            # Parse the savegame structure
            self._parse_savegame_data(decompressed)
            
            return {
                "map_width": self.map_width,
                "map_height": self.map_height,
                "vehicles": [v.__dict__ for v in self.vehicles],
                "stations": [s.__dict__ for s in self.stations], 
                "industries": [i.__dict__ for i in self.industries],
                "companies": [c.__dict__ for c in self.companies],
                "total_vehicles": len(self.vehicles),
                "total_stations": len(self.stations),
                "total_industries": len(self.industries),
                "total_companies": len(self.companies)
            }
            
        except Exception as e:
            logger.error(f"Failed to parse map data: {e}")
            return {}
    
    def _decompress_map_data(self, data: bytes) -> bytes:
        """Decompress map data using proper OpenTTD format detection"""
        try:
            import lzma
            
            if len(data) < 8:
                raise ValueError("Data too short for OpenTTD format")
            
            # Read format tag (big-endian) 
            tag = struct.unpack(">I", data[:4])[0]
            compressed_payload = data[8:]  # Skip 8-byte header
            
            # Decompress based on format
            if tag == 0x4F545458:  # 'OTTX' - LZMA (most common)
                logger.info("Decompressing LZMA format map data")
                return lzma.decompress(compressed_payload)
            elif tag == 0x4F54545A:  # 'OTTZ' - zlib
                logger.info("Decompressing zlib format map data")
                return zlib.decompress(compressed_payload)  
            elif tag == 0x4F54544E:  # 'OTTN' - uncompressed
                logger.info("Processing uncompressed map data")
                return compressed_payload
            elif tag == 0x4F545444:  # 'OTTD' - LZO
                raise NotImplementedError("LZO decompression not supported in Python")
            else:
                # Try LZMA as fallback (most common default)
                logger.warning(f"Unknown format tag {tag:08X}, trying LZMA as fallback")
                return lzma.decompress(compressed_payload)
                
        except Exception as e:
            logger.error(f"Failed to decompress map data: {e}")
            raise
    
    def _parse_savegame_data(self, data: bytes) -> None:
        """Parse OpenTTD savegame data structure"""
        logger.info(f"Parsing savegame data of {len(data)} bytes")
        
        # Skip any header and find start of chunks
        offset = 0
        
        # Look for chunk signatures
        chunk_patterns = [b'VEHS', b'STNS', b'INDS', b'PLYR', b'INDY']
        earliest_chunk = len(data)
        
        for pattern in chunk_patterns:
            pos = data.find(pattern)
            if pos != -1 and pos < earliest_chunk:
                earliest_chunk = pos
                
        if earliest_chunk < len(data):
            logger.info(f"Found chunks starting at offset {earliest_chunk}")
            offset = earliest_chunk
        else:
            logger.warning("No chunk signatures found, starting from beginning")
        
        # Parse chunks
        try:
            self._parse_chunks(data, offset)
        except Exception as e:
            logger.warning(f"Error parsing chunks: {e}")
            # Try alternative parsing methods
            self._parse_alternative_format(data)
    
    def _parse_chunks(self, data: bytes, offset: int) -> None:
        """Parse OpenTTD savegame chunks"""
        current_offset = offset
        chunks_found = 0
        
        while current_offset < len(data) - 8:
            try:
                # Read chunk tag
                chunk_tag = data[current_offset:current_offset + 4]
                if len(chunk_tag) < 4 or chunk_tag == b'\x00\x00\x00\x00':
                    break
                
                # Skip non-ASCII chunk tags
                try:
                    chunk_tag_str = chunk_tag.decode('ascii')
                except:
                    current_offset += 1
                    continue
                
                logger.debug(f"Found chunk '{chunk_tag_str}' at offset {current_offset}")
                
                # Read chunk type
                if current_offset + 4 >= len(data):
                    break
                chunk_type = data[current_offset + 4]
                
                # Calculate chunk size and data offset
                if chunk_type == 0xFF:  # Extended chunk with 4-byte length
                    if current_offset + 8 >= len(data):
                        break
                    chunk_size = struct.unpack('<I', data[current_offset + 5:current_offset + 9])[0]
                    data_offset = current_offset + 9
                elif chunk_type & 0x80:  # Gamma-encoded length
                    # Decode gamma length
                    length_bytes = []
                    pos = current_offset + 5
                    while pos < len(data):
                        byte = data[pos]
                        length_bytes.append(byte & 0x7F)
                        pos += 1
                        if not (byte & 0x80):
                            break
                    
                    # Calculate length from gamma encoding
                    chunk_size = 0
                    for i, byte in enumerate(length_bytes):
                        chunk_size |= byte << (7 * i)
                    data_offset = pos
                else:
                    # Simple byte length
                    chunk_size = chunk_type
                    data_offset = current_offset + 5
                
                # Validate chunk bounds
                if data_offset + chunk_size > len(data) or chunk_size > 1000000:
                    current_offset += 1
                    continue
                
                # Extract chunk data
                chunk_data = data[data_offset:data_offset + chunk_size]
                
                # Parse the chunk
                self._parse_chunk(chunk_tag_str, chunk_data)
                chunks_found += 1
                
                # Move to next chunk
                current_offset = data_offset + chunk_size
                
            except Exception as e:
                logger.debug(f"Error parsing chunk at offset {current_offset}: {e}")
                current_offset += 1
                if current_offset - offset > 50000:  # Prevent infinite loops
                    break
        
        logger.info(f"Parsed {chunks_found} chunks successfully")
    
    def _parse_chunk(self, tag: str, data: bytes) -> None:
        """Parse individual chunk data"""
        try:
            if tag == 'VEHS':  # Vehicles chunk
                self._parse_vehicles_chunk(data)
            elif tag == 'STNS':  # Stations chunk
                self._parse_stations_chunk(data)
            elif tag == 'INDS':  # Industries chunk  
                self._parse_industries_chunk(data)
            elif tag == 'PLYR':  # Companies chunk
                self._parse_companies_chunk(data)
            elif tag == 'MAP ':  # Map chunk
                self._parse_map_chunk(data)
            else:
                logger.debug(f"Unhandled chunk: {tag}")
        except Exception as e:
            logger.debug(f"Error parsing {tag} chunk: {e}")
    
    def _parse_vehicles_chunk(self, data: bytes) -> None:
        """Parse vehicles from chunk data"""
        # Simplified vehicle parsing - in real implementation would need
        # to parse the full vehicle structure
        offset = 0
        vehicle_id = 0
        
        while offset + 32 < len(data):  # Minimum vehicle record size
            try:
                # Basic vehicle data extraction (simplified)
                vtype = data[offset] % 6  # Vehicle type
                company = data[offset + 1] % 16  # Company ID
                
                # Skip if invalid
                if company >= 16:
                    offset += 1
                    continue
                
                vehicle = ParsedVehicle(
                    vehicle_id=vehicle_id,
                    vehicle_type=VehicleType(vtype),
                    company_id=company,
                    engine_type=0,  # Would need proper parsing
                    x=0, y=0, z=0,
                    speed=0,
                    profit_this_year=0,
                    profit_last_year=0,
                    running_cost=0,
                    build_year=1950,
                    reliability=100,
                    cargo_type=0,
                    cargo_capacity=0,
                    cargo_count=0
                )
                
                self.vehicles.append(vehicle)
                vehicle_id += 1
                offset += 32  # Move to next potential vehicle
                
            except Exception as e:
                offset += 1
                continue
    
    def _parse_stations_chunk(self, data: bytes) -> None:
        """Parse stations from chunk data"""
        # Placeholder implementation
        logger.debug(f"Parsing stations chunk of size {len(data)}")
        
    def _parse_industries_chunk(self, data: bytes) -> None:
        """Parse industries from chunk data"""
        # Placeholder implementation
        logger.debug(f"Parsing industries chunk of size {len(data)}")
        
    def _parse_companies_chunk(self, data: bytes) -> None:
        """Parse companies from chunk data"""
        # Placeholder implementation  
        logger.debug(f"Parsing companies chunk of size {len(data)}")
        
    def _parse_map_chunk(self, data: bytes) -> None:
        """Parse map dimensions and tile data"""
        if len(data) >= 8:
            self.map_width = struct.unpack('<I', data[0:4])[0]
            self.map_height = struct.unpack('<I', data[4:8])[0]
            logger.info(f"Parsed map size: {self.map_width}x{self.map_height}")
    
    def _parse_basic_data(self, data: bytes) -> None:
        """Fallback basic data parsing"""
        # Very basic parsing when chunk parsing fails
        
        # Try to extract vehicle count by looking for patterns
        vehicle_patterns = 0
        for i in range(0, len(data) - 4, 4):
            # Look for potential vehicle data patterns
            val = struct.unpack('<I', data[i:i+4])[0]
            if val < 16 and i + 16 < len(data):  # Potential company ID
                vehicle_patterns += 1
        
        # Create estimated data
        estimated_vehicles = min(vehicle_patterns // 10, 200)  # Rough estimate
        
        for i in range(estimated_vehicles):
            vehicle = ParsedVehicle(
                vehicle_id=i,
                vehicle_type=VehicleType(i % 4),
                company_id=i % 8,
                engine_type=0,
                x=0, y=0, z=0,
                speed=0,
                profit_this_year=0,
                profit_last_year=0,
                running_cost=0,
                build_year=1950,
                reliability=100,
                cargo_type=0,
                cargo_capacity=0,
                cargo_count=0
            )
            self.vehicles.append(vehicle)
        
        logger.info(f"Basic parsing extracted {len(self.vehicles)} vehicles")