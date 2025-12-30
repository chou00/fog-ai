#!/usr/bin/env python3
"""
Ryu SDN Controller for Fog-based AI Network Anomaly Detection

This controller:
- Collects flow statistics
- Communicates with Fog nodes
- Applies dynamic OpenFlow rules
- Blocks or limits suspicious traffic automatically
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp
from ryu.lib import hub
import json
import logging
import socket
import struct
from datetime import datetime
from collections import defaultdict


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FogAnomalyController(app_manager.RyuApp):
    """Ryu Controller for Fog-based Anomaly Detection"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(FogAnomalyController, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.flow_stats = defaultdict(dict)
        self.blocked_flows = set()
        self.fog_nodes = ['10.0.0.10', '10.0.0.11']  # Fog node IPs
        self.fog_socket = None
        self.monitor_thread = None
        self.log_file = 'logs/controller.log'
        self.mac_to_port = {}  # Initialize MAC learning table
        
        # Initialize logging directory
        import os
        os.makedirs('logs', exist_ok=True)
        
        # Start monitoring thread
        self.monitor_thread = hub.spawn(self._monitor_flows)
        
        logger.info("Fog Anomaly Controller initialized")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Handle switch features"""
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Install default table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        
        logger.info(f"Switch {datapath.id} connected")
        self.datapaths[datapath.id] = datapath
    
    def add_flow(self, datapath, priority, match, actions, buffer_id=None, hard_timeout=0):
        """Add a flow entry to switch"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        if buffer_id:
            mod = parser.OFPFlowMod(
                datapath=datapath, buffer_id=buffer_id,
                priority=priority, match=match,
                instructions=inst, hard_timeout=hard_timeout
            )
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath, priority=priority,
                match=match, instructions=inst, hard_timeout=hard_timeout
            )
        
        datapath.send_msg(mod)
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """Handle packet-in events"""
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        
        dst = eth.dst
        src = eth.src
        
        dpid = datapath.id
        
        # Learn MAC addresses
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port
        
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD
        
        actions = [parser.OFPActionOutput(out_port)]
        
        # Install flow entry
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        
        out = parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id,
            in_port=in_port, actions=actions, data=data
        )
        datapath.send_msg(out)
    
    def _monitor_flows(self):
        """Monitor flow statistics periodically"""
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(5)  # Request stats every 5 seconds
    
    def _request_stats(self, datapath):
        """Request flow statistics from switch"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)
        
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)
    
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        """Handle flow statistics reply"""
        body = ev.msg.body
        dpid = ev.msg.datapath.id
        
        stats = []
        for stat in body:
            stats.append({
                'dpid': dpid,
                'table_id': stat.table_id,
                'duration_sec': stat.duration_sec,
                'duration_nsec': stat.duration_nsec,
                'priority': stat.priority,
                'idle_timeout': stat.idle_timeout,
                'hard_timeout': stat.hard_timeout,
                'packet_count': stat.packet_count,
                'byte_count': stat.byte_count,
                'match': self._match_to_dict(stat.match),
            })
        
        # Store statistics
        self.flow_stats[dpid] = stats
        
        # Analyze and send to Fog nodes
        self._analyze_and_notify_fog(stats, dpid)
    
    def _match_to_dict(self, match):
        """Convert match to dictionary"""
        match_dict = {}
        for field in match.fields:
            match_dict[field.header] = field.value
        return match_dict
    
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        """Handle port statistics reply"""
        body = ev.msg.body
        dpid = ev.msg.datapath.id
        
        for stat in body:
            port_no = stat.port_no
            if port_no != 0xffffffff:  # Ignore OFPP_NONE
                logger.debug(f"Port {port_no} on switch {dpid}: "
                           f"rx_packets={stat.rx_packets}, "
                           f"tx_packets={stat.tx_packets}, "
                           f"rx_bytes={stat.rx_bytes}, "
                           f"tx_bytes={stat.tx_bytes}")
    
    def _analyze_and_notify_fog(self, stats, dpid):
        """Analyze flow statistics and notify Fog nodes"""
        for stat in stats:
            # Check for suspicious patterns
            flow_key = (
                stat['match'].get('ipv4_src', ''),
                stat['match'].get('ipv4_dst', ''),
                stat['match'].get('tcp_src', ''),
                stat['match'].get('tcp_dst', '')
            )
            
            # High packet rate detection
            if stat['packet_count'] > 10000 and stat['duration_sec'] < 10:
                if flow_key not in self.blocked_flows:
                    logger.warning(f"Suspicious flow detected: {flow_key}")
                    # Get datapath from stored datapaths
                    datapath = self.datapaths.get(dpid)
                    if datapath:
                        self._block_flow(datapath, stat['match'])
                        self.blocked_flows.add(flow_key)
            
            # Send statistics to Fog nodes
            self._send_to_fog_node(stat)
    
    def _block_flow(self, datapath, match_dict):
        """Block a suspicious flow"""
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        
        # Create match
        match = parser.OFPMatch(**match_dict)
        
        # No actions = drop
        actions = []
        
        # Add drop flow with high priority
        self.add_flow(datapath, 100, match, actions, hard_timeout=300)
        
        logger.warning(f"Blocked flow: {match_dict}")
        self._log_event('block', match_dict)
    
    def _send_to_fog_node(self, stat):
        """Send statistics to Fog nodes for analysis"""
        # In a real implementation, this would send data via socket/API
        # For simulation, we'll log it
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'flow_stat',
            'data': stat
        }
        self._log_event('flow_stat', stat)
    
    def _log_event(self, event_type, data):
        """Log events to file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write log: {e}")
    


if __name__ == '__main__':
    from ryu.cmd import manager
    manager.main()

